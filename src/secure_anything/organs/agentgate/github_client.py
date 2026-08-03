"""GitHub REST client: fetch a PR's changed files, post the gate outcome, and
run the human-approval loop.

Auth is via a GitHub App **installation token** in production (a short-lived token
minted from the App's private key). With no App credentials (dev), calls degrade to a
logged no-op so the pipeline still runs end-to-end offline.

Every network boundary is an injectable seam: pass an ``httpx.Client`` (e.g. one built
on ``httpx.MockTransport``) and a ``token_provider`` to exercise the real request-
building code in tests without a key or a network — the same discipline as the checks.
"""
from __future__ import annotations

import logging
import time
from typing import Callable

import httpx

from .config import Settings
from .domain import ActionType, ChangeSet, Decision, FileChange, PullRequest

log = logging.getLogger("agentgate.github")

# check-run conclusions per gate action; escalate/request-changes must NOT be "success"
# so branch protection ("require the AgentGate check") keeps the PR unmergeable.
_CONCLUSION = {
    ActionType.AUTO_APPROVE: "success",
    ActionType.REQUEST_CHANGES: "failure",
    ActionType.ESCALATE: "action_required",
}
_REVIEW_EVENT = {
    ActionType.AUTO_APPROVE: "APPROVE",
    ActionType.REQUEST_CHANGES: "REQUEST_CHANGES",
    ActionType.ESCALATE: "COMMENT",
}
CHECK_NAME = "AgentGate"
# repo permission levels that may approve an escalated PR (authorization, not just auth).
APPROVE_PERMISSIONS = {"admin", "maintain", "write"}


class GitHubClient:
    def __init__(
        self,
        settings: Settings,
        *,
        client: httpx.Client | None = None,
        token_provider: Callable[[], str] | None = None,
    ):
        self.settings = settings
        self._client = client
        self._token_provider = token_provider
        self._cached_token = ""
        self._token_exp = 0.0  # epoch seconds; re-mint before this

    # ---- auth ---------------------------------------------------------------
    def _token(self) -> str:
        """Return a usable installation token, or "" when unauthenticated (dev)."""
        if self._token_provider is not None:
            return self._token_provider()
        if not self.settings.github_app_ready:
            return ""
        if self._cached_token and time.time() < self._token_exp - 60:
            return self._cached_token
        self._cached_token, self._token_exp = self._mint_installation_token()
        return self._cached_token

    def _app_jwt(self) -> str:
        """Sign a short-lived App JWT (RS256) from the App private key.

        Requires the optional ``[github]`` extra (``pyjwt[crypto]``); raises an
        honest error rather than faking a token if it is missing.
        """
        try:
            import jwt  # from pyjwt[crypto]; optional extra
        except ImportError as exc:  # pragma: no cover - exercised only in prod
            raise RuntimeError(
                "GitHub App auth needs the optional dependency: pip install '.[github]'"
            ) from exc
        key = open(self.settings.github_app_private_key_path).read()  # noqa: SIM115
        now = int(time.time())
        payload = {"iat": now - 60, "exp": now + 540, "iss": self.settings.github_app_id}
        return jwt.encode(payload, key, algorithm="RS256")

    def _mint_installation_token(self) -> tuple[str, float]:  # pragma: no cover - needs key
        url = (
            f"{self.settings.github_api_base}"
            f"/app/installations/{self.settings.github_app_installation_id}/access_tokens"
        )
        headers = {
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {self._app_jwt()}",
        }
        with self._http() as client:
            resp = client.post(url, headers=headers)
            resp.raise_for_status()
            data = resp.json()
        # tokens live ~1h; cache with a conservative 50-min TTL.
        return data["token"], time.time() + 50 * 60

    # ---- transport ----------------------------------------------------------
    def _http(self) -> httpx.Client:
        return self._client or httpx.Client(timeout=20)

    def _headers(self) -> dict:
        h = {"Accept": "application/vnd.github+json"}
        token = self._token()
        if token:
            h["Authorization"] = f"Bearer {token}"
        return h

    # ---- reads --------------------------------------------------------------
    def fetch_changeset(self, repo: str, number: int) -> ChangeSet:
        """GET the PR's changed files, following pagination (100/page)."""
        if not self._token():
            log.info("no github token; returning empty changeset for %s#%s", repo, number)
            return ChangeSet()
        url = f"{self.settings.github_api_base}/repos/{repo}/pulls/{number}/files"
        files: list[FileChange] = []
        # First page carries per_page; subsequent requests must pass params=None so
        # httpx preserves the cursor already embedded in the "next" URL (passing an
        # empty dict overwrites the query string and re-fetches page 1 forever).
        params: dict | None = {"per_page": 100}
        client = self._http()
        try:
            for _ in range(200):  # defensive cap: 200 pages * 100 = 20k files
                resp = client.get(url, headers=self._headers(), params=params)
                resp.raise_for_status()
                for f in resp.json():
                    files.append(FileChange(
                        path=f.get("filename", ""),
                        additions=f.get("additions", 0),
                        deletions=f.get("deletions", 0),
                        patch=f.get("patch", "") or "",
                    ))
                nxt = resp.links.get("next")
                if not nxt:
                    break
                url = nxt["url"]
                params = None  # the "next" url already carries the cursor
            else:
                log.warning("fetch_changeset hit page cap for %s#%s", repo, number)
        finally:
            if self._client is None:
                client.close()
        return ChangeSet(files=files)

    def head_sha(self, repo: str, number: int) -> str:
        """The current head SHA of a PR (needed to attach a check-run)."""
        url = f"{self.settings.github_api_base}/repos/{repo}/pulls/{number}"
        client = self._http()
        try:
            resp = client.get(url, headers=self._headers())
            resp.raise_for_status()
            return (resp.json().get("head") or {}).get("sha", "")
        finally:
            if self._client is None:
                client.close()

    def permission_level(self, repo: str, login: str) -> str:
        """The repo permission of a user: admin|maintain|write|triage|read|none."""
        url = f"{self.settings.github_api_base}/repos/{repo}/collaborators/{login}/permission"
        client = self._http()
        try:
            resp = client.get(url, headers=self._headers())
            if resp.status_code == 404:
                return "none"
            resp.raise_for_status()
            return resp.json().get("permission", "none")
        finally:
            if self._client is None:
                client.close()

    # ---- writes -------------------------------------------------------------
    def post_decision(self, pr: PullRequest, decision: Decision, *, audit_id: str = "") -> None:
        """Post the gate outcome: a check-run (which gates merge) + a PR review + a comment.

        auto_approve -> success/APPROVE; request_changes -> failure/REQUEST_CHANGES;
        escalate -> action_required/COMMENT (blocks merge, pings a human).
        No-op with a log line when unauthenticated (dev).
        """
        if not self._token():
            log.info(
                "would post %s (risk=%s) to %s#%s: %s",
                decision.action.value, decision.risk.value, pr.repo, pr.number, decision.reasons,
            )
            return
        sha = pr.head_sha or self.head_sha(pr.repo, pr.number)
        summary = _decision_summary(decision, audit_id)
        client = self._http()
        try:
            self._check_run(client, pr.repo, sha, _CONCLUSION[decision.action], summary)
            self._review(client, pr.repo, pr.number, _REVIEW_EVENT[decision.action], summary)
            self._comment(client, pr.repo, pr.number, summary)
        finally:
            if self._client is None:
                client.close()

    def approve(self, cmd_repo: str, number: int, sha: str, approver: str,
                *, audit_id: str = "") -> None:
        """Flip the AgentGate check to success and comment, after a human approved."""
        if not self._token():
            log.info("would approve %s#%s (by %s)", cmd_repo, number, approver)
            return
        body = (
            f"✅ **AgentGate: approved by @{approver}** (write access verified). "
            f"Merge unblocked.\n\nAudit id: `{audit_id or 'n/a'}`."
        )
        client = self._http()
        try:
            self._check_run(client, cmd_repo, sha, "success",
                            f"Approved by @{approver}. Audit id: {audit_id or 'n/a'}.")
            self._comment(client, cmd_repo, number, body)
        finally:
            if self._client is None:
                client.close()

    def refuse_approval(self, repo: str, number: int, commenter: str, level: str) -> None:
        """Comment that an approval was refused for lack of write access."""
        if not self._token():
            log.info("would refuse approval %s#%s by %s (permission=%s)",
                     repo, number, commenter, level)
            return
        client = self._http()
        try:
            self._comment(
                client, repo, number,
                f"⛔ @{commenter} lacks write access (permission: `{level}`); approval "
                "refused. This attempt is recorded in the audit ledger.",
            )
        finally:
            if self._client is None:
                client.close()

    # ---- write helpers ------------------------------------------------------
    def _check_run(self, client, repo, sha, conclusion, summary) -> None:
        # Re-posting the same (name, head_sha) with a new conclusion updates the check,
        # which is how an approval flips an earlier action_required to success.
        client.post(
            f"{self.settings.github_api_base}/repos/{repo}/check-runs",
            headers=self._headers(),
            json={"name": CHECK_NAME, "head_sha": sha, "status": "completed",
                  "conclusion": conclusion,
                  "output": {"title": f"AgentGate: {conclusion}", "summary": summary}},
        ).raise_for_status()

    def _review(self, client, repo, number, event, body) -> None:
        client.post(
            f"{self.settings.github_api_base}/repos/{repo}/pulls/{number}/reviews",
            headers=self._headers(), json={"event": event, "body": body},
        ).raise_for_status()

    def _comment(self, client, repo, number, body) -> None:
        client.post(
            f"{self.settings.github_api_base}/repos/{repo}/issues/{number}/comments",
            headers=self._headers(), json={"body": body},
        ).raise_for_status()


def _decision_summary(decision: Decision, audit_id: str) -> str:
    lines = [f"**AgentGate decision: `{decision.action.value}`** (risk: {decision.risk.value})"]
    if decision.reasons:
        lines.append("")
        lines.extend(f"- {r}" for r in decision.reasons)
    if decision.action is ActionType.ESCALATE:
        lines.append("")
        lines.append("A human with write access can approve by commenting `/agentgate approve`.")
    if audit_id:
        lines.append("")
        lines.append(f"Audit id: `{audit_id}`")
    return "\n".join(lines)
