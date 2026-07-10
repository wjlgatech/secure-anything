"""The evaluation pipeline: checks -> optional LLM review -> decision -> audit ->
persist -> post back to GitHub. `evaluate()` is the pure core (no I/O) used by tests;
`process_job()` wires in the datastore + GitHub; `run()` is the worker loop."""
from __future__ import annotations

import logging
import time

from sqlalchemy import select

from .config import Settings, get_settings
from .decision import decide
from .domain import ChangeSet, Decision, PullRequest
from .github_client import GitHubClient
from .models import PRReview
from .policy.engine import load_policy
from .policy.schema import Policy
from .review import llm_review
from .review.llm_review import LLMReview
from .checks.registry import default_checks

log = logging.getLogger("agentgate.worker")


def evaluate(
    pr: PullRequest,
    changes: ChangeSet,
    policy: Policy,
    settings: Settings | None = None,
    llm: LLMReview | None = None,
) -> Decision:
    """Run every check, optionally an LLM review, and return the gate Decision.
    Pure and deterministic given (pr, changes, policy) with no LLM key set."""
    results = [c.run(pr, changes, policy) for c in default_checks()]

    llm_expected = bool(settings and settings.llm_review_enabled)
    review = llm
    if review is None and llm_expected:
        try:
            review = llm_review.review(pr, changes, settings)  # may return None
        except Exception as exc:  # unavailable -> honest escalation downstream
            log.warning("llm review failed, treating as unavailable: %s", exc)
            review = None

    return decide(pr, results, policy, llm=review, llm_expected=llm_expected)


def process_job(job: dict, *, session, policy: Policy, settings: Settings,
                github: GitHubClient | None = None) -> Decision | None:
    from .audit import AuditLedger

    pr = PullRequest.model_validate(job["pr"])

    # idempotency: one decision per webhook delivery
    if pr.delivery_id:
        existing = session.execute(
            select(PRReview).where(PRReview.delivery_id == pr.delivery_id)
        ).scalar_one_or_none()
        if existing:
            log.info("delivery %s already processed; skipping", pr.delivery_id)
            return None

    gh = github or GitHubClient(settings)
    changes = gh.fetch_changeset(pr.repo, pr.number)
    decision = evaluate(pr, changes, policy, settings=settings)

    event = AuditLedger(session).append("pr_decision", {
        "repo": pr.repo, "number": pr.number, "delivery_id": pr.delivery_id,
        "actor": pr.actor.model_dump(), "action": decision.action.value,
        "risk": decision.risk.value, "reasons": decision.reasons,
    })
    session.add(PRReview(
        delivery_id=pr.delivery_id or f"{pr.repo}#{pr.number}",
        repo=pr.repo, number=pr.number,
        actor_login=pr.actor.login, actor_kind=pr.actor.kind.value,
        action=decision.action.value, risk=decision.risk.value,
        reasons="; ".join(decision.reasons),
    ))
    session.commit()

    gh.post_decision(pr, decision, audit_id=event.hash)
    return decision


def handle_job(job: dict, *, session, policy: Policy, settings: Settings,
               github: GitHubClient | None = None):
    """Dispatch a dequeued job by kind: a PR review or a human approval command."""
    if job.get("kind") == "approval":
        from .approvals import process_approval
        from .domain import ApprovalCommand

        cmd = ApprovalCommand.model_validate(job["approval"])
        return process_approval(cmd, session=session, settings=settings, github=github)
    return process_job(job, session=session, policy=policy, settings=settings, github=github)


def run() -> None:  # pragma: no cover - long-running loop
    from .db import session_factory
    from .queue import get_queue

    settings = get_settings()
    policy = load_policy(settings.policy_path)
    q = get_queue(settings)
    Session = session_factory()
    log.info("worker started (queue=%s)", settings.queue_backend)
    while True:
        job = q.dequeue()
        if job is None:
            time.sleep(1)
            continue
        try:
            with Session() as session:
                handle_job(job, session=session, policy=policy, settings=settings)
        except Exception:
            log.exception("job failed")


if __name__ == "__main__":  # pragma: no cover
    logging.basicConfig(level=get_settings().log_level)
    run()
