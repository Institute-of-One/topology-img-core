"""The release metadata must agree with itself, and with what this archive claims to be.

This repository is published as a research record rather than as supplementary material to
a paper, so its metadata is not a formality attached to a manuscript -- it is the citation.
When `pyproject.toml`, `CITATION.cff` and `.zenodo.json` disagree, the citation a reader
follows is the one that is wrong, and there is no accompanying article to correct it.

They already disagreed: CITATION.cff said 0.2.0 while pyproject.toml said 0.1.0, and neither
matched a repository that had completed Phase 2. Nothing caught it because nothing was
looking.

The last two checks are about honesty rather than consistency. An archive offered as a
negative research record has to say that it is one, and has to keep the reason it was not
written up separate from the fact that its result was negative. A record that let those run
together would be publication bias with a DOI attached.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

try:  # tomllib is standard-library from Python 3.11
    import tomllib
except ModuleNotFoundError:  # pragma: no cover
    import tomli as tomllib

REPO = Path(__file__).resolve().parents[1]
PYPROJECT = REPO / "pyproject.toml"
CITATION = REPO / "CITATION.cff"
ZENODO = REPO / ".zenodo.json"
README = REPO / "README.md"

REPO_URL = "https://github.com/Institute-of-One/topology-img-core"


def _pyproject() -> dict:
    return tomllib.loads(PYPROJECT.read_text(encoding="utf-8"))


def _citation_version() -> str:
    text = CITATION.read_text(encoding="utf-8")
    match = re.search(r"^version:\s*\"?([^\"\n]+)\"?\s*$", text, flags=re.MULTILINE)
    assert match, "CITATION.cff declares no version"
    return match.group(1).strip()


def _zenodo() -> dict:
    return json.loads(ZENODO.read_text(encoding="utf-8"))


def test_the_version_is_the_same_in_every_declaration():
    version = _pyproject()["project"]["version"]
    assert _citation_version() == version, (
        f"CITATION.cff says {_citation_version()}, pyproject.toml says {version}"
    )
    assert _zenodo()["version"] == version, (
        f".zenodo.json says {_zenodo()['version']}, pyproject.toml says {version}"
    )


def test_the_licence_is_mit_in_every_declaration():
    licence = _pyproject()["project"].get("license")
    if isinstance(licence, dict):
        licence = licence.get("text")
    assert licence in ("MIT", None), licence
    assert "license: MIT" in CITATION.read_text(encoding="utf-8")
    assert _zenodo()["license"] == "MIT"


def test_the_repository_is_named_once_and_correctly():
    citation = CITATION.read_text(encoding="utf-8")
    assert REPO_URL in citation
    related = [item["identifier"] for item in _zenodo().get("related_identifiers", [])]
    assert REPO_URL in related
    organisations = set(re.findall(r"github\.com/([A-Za-z0-9_.-]+)", README.read_text(encoding="utf-8")))
    assert organisations <= {"Institute-of-One"}, f"unexpected organisations: {organisations}"


def test_no_zenodo_doi_is_recorded_as_a_top_level_doi():
    """A top-level doi tells Zenodo the DOI came from elsewhere and stops it versioning.

    The concept DOI belongs in related_identifiers as isVersionOf, once minted.
    """
    assert "doi" not in _zenodo(), (
        "a top-level 'doi' in .zenodo.json stops Zenodo minting version DOIs; record the "
        "concept DOI as an isVersionOf relation instead"
    )


def test_the_archive_says_it_is_a_negative_record_rather_than_a_paper():
    """An archive offered instead of a manuscript has to say so where a reader will look."""
    description = _zenodo()["description"].lower()
    readme = README.read_text(encoding="utf-8").lower()
    for phrase in ("negative", "preregist"):
        assert phrase in description, f"the Zenodo description does not mention {phrase!r}"
    # Not an `or` over the two places the README says this. It says it twice, in the header
    # and in the section, and an `or` passed happily when the header sentence was replaced
    # with "a manuscript is in preparation" -- which is the exact defect this test exists to
    # catch. Injection found that; reading the test did not.
    assert "this repository is the publication" in readme, (
        "the README no longer states plainly that the archive itself is the publication"
    )
    assert "there is no manuscript" in readme, (
        "the README no longer says that no paper accompanies this record"
    )
    assert "no manuscript was written" in description, (
        "the Zenodo description no longer says that no paper accompanies this record"
    )
    for claim in ("manuscript is in preparation", "manuscript in preparation",
                  "paper is forthcoming", "will be submitted"):
        assert claim not in readme, (
            f"the README promises a manuscript ({claim!r}); this archive is offered instead "
            f"of one, and a promised paper turns a published record back into a placeholder"
        )


def test_the_reason_for_not_publishing_is_kept_separate_from_the_result_being_negative():
    """The one sentence this record cannot afford to lose.

    "We did not publish because it was negative" is the bias this archive exists to avoid.
    The result being negative and the decision not to write a manuscript are different
    facts with different reasons, and both documents must keep them apart.
    """
    for path in (README, ZENODO):
        text = path.read_text(encoding="utf-8").lower()
        assert "not because the result is negative" in text, (
            f"{path.name} does not separate the negative result from the decision not to "
            f"write a manuscript; without that sentence this archive reads as a drawer"
        )


def test_the_preregistration_documents_are_present():
    docs = REPO / "docs"
    required = [
        "phase2_preregistration_v1.0.md",
        "finite_size_scaling_findings.md",
        "exploratory_anatomical_background_protocol.md",
    ]
    missing = [name for name in required if not (docs / name).is_file()]
    assert not missing, f"the record is incomplete without: {missing}"


def test_the_unexecuted_protocol_says_it_was_not_executed():
    """A frozen protocol with no result looks like a hidden one unless it says otherwise."""
    text = (REPO / "docs" / "exploratory_anatomical_background_protocol.md").read_text(
        encoding="utf-8"
    ).lower()
    assert "not executed" in text and "never produced" in text, (
        "the frozen exploratory protocol does not record that it was deliberately not run"
    )
