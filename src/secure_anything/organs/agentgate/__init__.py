"""AgentGate — the trust & accountability gate for human + AI-agent code changes.

First wedge: a PR firewall for coding agents. Every pull request (from a human OR
an AI coding agent) passes a policy gate that runs deterministic checks + optional
LLM risk review, auto-approves the safe ones, routes risky ones to human approval,
and writes an immutable, tamper-evident audit trail.
"""

__version__ = "0.1.0"
