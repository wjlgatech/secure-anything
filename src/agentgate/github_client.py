"""Thin GitHub REST client: fetch a PR's changed files, post the gate outcome.

Auth is via the GitHub App installation token in production. With no credentials
(dev), calls degrade to a logged no-op so the pipeline still runs end-to-end.
"""
from __future__ import annotations

import logging

import httpx

from .config import Settings
from .domain import ChangeSet, Decision, FileChange, PullRequest

log = logging.getLogger("agentgate.github")


class GitHubClient:
    def __init__(self, settings: Settings):
        self.settings = settings
        self._token = ""  # in prod: mint an installation token from the App key

    def _headers(self) -> dict:
        h = {"Accept": "application/vnd.github+json"}
        if self._token:
            h["Authorization"] = f"Bearer {self._token}"
        return h

    def fetch_changeset(self, repo: str, number: int) -> ChangeSet:
        if not self._token:
            log.info("no github token; returning empty changeset for %s#%s", repo, number)
            return ChangeSet()
        url = f"{self.settings.github_api_base}/repos/{repo}/pulls/{number}/files"
        files: list[FileChange] = []
        with httpx.Client(timeout=20) as client:
            resp = client.get(url, headers=self._headers(), params={"per_page": 100})
            resp.raise_for_status()
            for f in resp.json():
                files.append(FileChange(
                    path=f.get("filename", ""),
                    additions=f.get("additions", 0),
                    deletions=f.get("deletions", 0),
                    patch=f.get("patch", "") or "",
                ))
        return ChangeSet(files=files)

    def post_decision(self, pr: PullRequest, decision: Decision) -> None:
        """Post a check-run + review reflecting the gate decision.

        auto_approve -> approving review; request_changes -> changes-requested;
        escalate -> a neutral check that blocks merge and pings human reviewers.
        No-op with a log line when unauthenticated.
        """
        if not self._token:
            log.info(
                "would post %s (risk=%s) to %s#%s: %s",
                decision.action.value, decision.risk.value, pr.repo, pr.number, decision.reasons,
            )
            return
        # Production: POST /repos/{repo}/check-runs and /pulls/{n}/reviews here.
        raise NotImplementedError("wire GitHub check-run + review posting for production")
