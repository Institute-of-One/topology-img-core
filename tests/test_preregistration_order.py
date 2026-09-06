import json
from pathlib import Path
import subprocess


ROOT = Path(__file__).resolve().parents[1]


def git(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["git", "-C", str(ROOT), *args], text=True,
                          capture_output=True, check=False)


def test_phase2_data_descends_from_frozen_preregistration():
    provenance = json.loads((ROOT / "provenance" / "phase2_commits.json").read_text(encoding="utf-8"))
    freeze = provenance["freeze_commit"]
    data = provenance["first_phase2_data_commit"]
    for commit in (freeze, data):
        assert git("cat-file", "-e", f"{commit}^{{commit}}").returncode == 0, (
            f"Required commit {commit} is unavailable. CI must checkout with fetch-depth: 0."
        )
    ancestry = git("merge-base", "--is-ancestor", freeze, data)
    assert ancestry.returncode == 0, f"Freeze {freeze} is not an ancestor of data {data}."


def test_freeze_commit_contains_only_preregistration():
    provenance = json.loads((ROOT / "provenance" / "phase2_commits.json").read_text(encoding="utf-8"))
    changed = git("diff-tree", "--no-commit-id", "--name-only", "-r", provenance["freeze_commit"])
    assert changed.returncode == 0, changed.stderr
    assert changed.stdout.splitlines() == [provenance["preregistration_path"]]


def test_seed_amendments_precede_seed_data():
    provenance = json.loads((ROOT / "provenance" / "phase2_commits.json").read_text(encoding="utf-8"))
    data = provenance["seed_sensitivity_data_commit"]
    for key in ("seed_amendment_v1_1_commit", "boundary_amendment_v1_2_commit"):
        amendment = provenance[key]
        assert git("cat-file", "-e", f"{amendment}^{{commit}}").returncode == 0
        assert git("merge-base", "--is-ancestor", amendment, data).returncode == 0, (
            f"Amendment {amendment} must precede seed data {data}."
        )
