from secure_anything.organs.agentgate.checks.diff_size import DiffSizeCheck
from secure_anything.organs.agentgate.checks.paths import path_matches
from secure_anything.organs.agentgate.checks.secret_scan import SecretScanCheck
from secure_anything.organs.agentgate.checks.touched_paths import TouchedPathsCheck
from secure_anything.organs.agentgate.domain import RiskTier


def test_diff_size_tiers(make_pr, make_changes, policy):
    chk = DiffSizeCheck()
    small = make_changes([{"path": "a.py", "additions": 10, "deletions": 5}])
    assert chk.run(make_pr(), small, policy).passed

    medium = make_changes([{"path": "a.py", "additions": 900, "deletions": 0}])
    r = chk.run(make_pr(), medium, policy)
    assert not r.passed and r.severity is RiskTier.MEDIUM

    huge = make_changes([{"path": "a.py", "additions": 4000, "deletions": 0}])
    r = chk.run(make_pr(), huge, policy)
    assert not r.passed and r.severity is RiskTier.HIGH


def test_secret_scan_detects_and_blocks(make_pr, make_changes, policy):
    diff = "+AWS_KEY = 'AKIAIOSFODNN7EXAMPLE'\n+some_ok = 1"
    changes = make_changes([{"path": "cfg.py", "patch": diff, "additions": 2}])
    r = SecretScanCheck().run(make_pr(), changes, policy)
    assert not r.passed and r.blocking and r.severity is RiskTier.HIGH


def test_secret_scan_clean(make_pr, make_changes, policy):
    changes = make_changes([{"path": "a.py", "patch": "+x = 1\n+y = 2", "additions": 2}])
    assert SecretScanCheck().run(make_pr(), changes, policy).passed


def test_touched_paths(make_pr, make_changes, policy):
    protected = make_changes([{"path": ".github/workflows/ci.yml", "additions": 3}])
    r = TouchedPathsCheck().run(make_pr(), protected, policy)
    assert not r.passed and r.severity is RiskTier.HIGH

    ok = make_changes([{"path": "src/feature.py", "additions": 3}])
    assert TouchedPathsCheck().run(make_pr(), ok, policy).passed


def test_path_matches():
    assert path_matches(".github/workflows/ci.yml", ".github/workflows/**")
    assert path_matches("services/api/Dockerfile", "**/Dockerfile")
    assert path_matches("Dockerfile", "**/Dockerfile")  # root-level too
    assert not path_matches("src/app.py", "**/auth/**")
    assert path_matches("src/auth/token.py", "**/auth/**")
