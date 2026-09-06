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


def test_resource_gate_commit_contains_only_supplement():
    provenance = json.loads((ROOT / "provenance" / "phase2_commits.json").read_text(encoding="utf-8"))
    freeze = provenance["resource_gate_commit"]
    assert git("cat-file", "-e", f"{freeze}^{{commit}}").returncode == 0, (
        f"Required commit {freeze} is unavailable. CI must checkout with fetch-depth: 0."
    )
    changed = git("diff-tree", "--no-commit-id", "--name-only", "-r", freeze)
    assert changed.returncode == 0, changed.stderr
    assert changed.stdout.splitlines() == [provenance["resource_gate_path"]]


def test_resource_gate_precedes_n192_data_when_registered():
    provenance = json.loads((ROOT / "provenance" / "phase2_commits.json").read_text(encoding="utf-8"))
    data = provenance.get("n192_resource_data_commit")
    if data is None:
        return

    freeze = provenance["resource_gate_commit"]
    for commit in (freeze, data):
        assert git("cat-file", "-e", f"{commit}^{{commit}}").returncode == 0, (
            f"Required commit {commit} is unavailable. CI must checkout with fetch-depth: 0."
        )
    assert git("merge-base", "--is-ancestor", freeze, data).returncode == 0, (
        f"Resource-gate freeze {freeze} must precede N=192 data {data}."
    )


def test_resource_gate_precedes_refined_calibration_data():
    provenance = json.loads((ROOT / "provenance" / "phase2_commits.json").read_text(encoding="utf-8"))
    freeze = provenance["resource_gate_commit"]
    data = provenance["refined_n64_n96_data_commit"]
    assert git("merge-base", "--is-ancestor", freeze, data).returncode == 0, (
        f"Resource-gate freeze {freeze} must precede calibration data {data}."
    )


def test_scaling_precision_amendment_is_frozen_before_extension_data():
    provenance = json.loads((ROOT / "provenance" / "phase2_commits.json").read_text(encoding="utf-8"))
    amendment = provenance["scaling_precision_amendment_commit"]
    data = provenance["scaling_precision_data_commit"]
    for commit in (amendment, data):
        assert git("cat-file", "-e", f"{commit}^{{commit}}").returncode == 0, (
            f"Required commit {commit} is unavailable. CI must checkout with fetch-depth: 0."
        )
    changed = git("diff-tree", "--no-commit-id", "--name-only", "-r", amendment)
    assert changed.returncode == 0, changed.stderr
    assert changed.stdout.splitlines() == [provenance["scaling_precision_amendment_path"]]
    assert git("merge-base", "--is-ancestor", amendment, data).returncode == 0, (
        f"Scaling-precision amendment {amendment} must precede extension data {data}."
    )


def test_resource_gate_decision_precedes_n256_data():
    provenance = json.loads((ROOT / "provenance" / "phase2_commits.json").read_text(encoding="utf-8"))
    decision = provenance["resource_gate_decision_commit"]
    data = provenance["n256_data_commit"]
    for commit in (decision, data):
        assert git("cat-file", "-e", f"{commit}^{{commit}}").returncode == 0, (
            f"Required commit {commit} is unavailable. CI must checkout with fetch-depth: 0."
        )
    assert git("merge-base", "--is-ancestor", decision, data).returncode == 0, (
        f"Resource-gate decision {decision} must precede N=256 data {data}."
    )


def test_all_scaling_freezes_precede_scaling_outcome():
    provenance = json.loads((ROOT / "provenance" / "phase2_commits.json").read_text(encoding="utf-8"))
    data = provenance["finite_size_scaling_data_commit"]
    freezes = (
        provenance["freeze_commit"],
        provenance["seed_amendment_v1_1_commit"],
        provenance["boundary_amendment_v1_2_commit"],
        provenance["resource_gate_commit"],
        provenance["scaling_precision_amendment_commit"],
    )
    for commit in (*freezes, data):
        assert git("cat-file", "-e", f"{commit}^{{commit}}").returncode == 0, (
            f"Required commit {commit} is unavailable. CI must checkout with fetch-depth: 0."
        )
    for freeze in freezes:
        assert git("merge-base", "--is-ancestor", freeze, data).returncode == 0, (
            f"Scaling freeze {freeze} must precede scaling outcome {data}."
        )
