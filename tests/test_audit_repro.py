"""Tests for `heddle_workspace.audit_repro` — the reproducibility scorer.

The load-bearing test is `test_run0_baseline_reproduces_comparison_verdict`:
fed the run-1 and run-2 finding fixtures (faithfully extracted from the
2026-05-19 archived audits, authority = the verified comparison doc), the
scorer must reproduce that doc's verdict — a stable core of ~13-15 findings,
~4-5 divergences each way, and a median Jaccard well below the proposed bar.
If this fails, the matcher is the problem, not the audit-runner.
"""

from __future__ import annotations

from pathlib import Path

from heddle_workspace import audit_repro as ar
from heddle_workspace.audit_repro import Finding

FIXTURES = Path(__file__).parent / "fixtures" / "audit_repro"


# --- scorer arithmetic ----------------------------------------------------


def test_identical_runs_score_perfect() -> None:
    run = [Finding("a", "f.py", 10, "high"), Finding("b", "g.py", 20, "low")]
    m = ar.match_runs(run, list(run))
    assert len(m.agreed) == 2
    assert m.jaccard() == 1.0
    assert m.jaccard(high_only=True) == 1.0


def test_disjoint_runs_score_zero() -> None:
    a = [Finding("a", "f.py", 10)]
    b = [Finding("b", "g.py", 10)]
    m = ar.match_runs(a, b)
    assert m.agreed == []
    assert m.jaccard() == 0.0


def test_line_window_tolerates_drift_but_not_far_apart() -> None:
    a = [Finding("x", "f.py", 100)]
    near = [Finding("x", "f.py", 110)]
    far = [Finding("x", "f.py", 200)]
    assert ar.match_runs(a, near, line_window=25).jaccard() == 1.0
    assert ar.match_runs(a, far, line_window=25).jaccard() == 0.0


def test_none_line_matches_on_file_and_concern() -> None:
    a = [Finding("suite", "tests/", None)]
    b = [Finding("suite", "tests/", None)]
    assert ar.match_runs(a, b).jaccard() == 1.0


def test_opposite_stance_is_contradiction_not_agreement() -> None:
    a = [Finding("cas", "f.py", 73, "high", stance="ok")]
    b = [Finding("cas", "f.py", 73, "high", stance="finding")]
    m = ar.match_runs(a, b)
    assert m.agreed == []
    assert len(m.contradictions) == 1
    # contradiction counts toward the union but never the intersection
    assert m.jaccard() == 0.0


def test_high_only_jaccard_ignores_low_severity() -> None:
    a = [Finding("a", "f.py", 1, "high"), Finding("b", "g.py", 1, "low")]
    b = [Finding("a", "f.py", 1, "high")]
    m = ar.match_runs(a, b)
    assert m.jaccard(high_only=True) == 1.0  # the one high finding agrees
    assert m.jaccard() == 0.5  # but the low-sev finding is only in run a


# --- ingestion ------------------------------------------------------------


def test_load_findings_block_from_markdown(tmp_path: Path) -> None:
    report = tmp_path / "audit.md"
    report.write_text(
        "# audit\n\nsome prose\n\n"
        "```findings\n"
        '[{"concern_key": "x", "file": "f.py", "line": 5, "severity": "high"}]\n'
        "```\n\nmore prose\n"
    )
    findings = ar.load_findings(report)
    assert len(findings) == 1
    assert findings[0].concern_key == "x"
    assert findings[0].is_high


# --- run-0 baseline -------------------------------------------------------


def test_run0_concern_only_reproduces_comparison_verdict() -> None:
    """Concern-only matching (≈ human semantic match) reproduces the comparison
    doc's verdict exactly: 13 stable-core, 4 missed each way, 1 contradiction."""
    run1 = ar.load_findings(FIXTURES / "run-1.findings.json")
    run2 = ar.load_findings(FIXTURES / "run-2.findings.json")
    m = ar.match_runs(run1, run2, require_file=False)

    # Stable core both runs agreed on (comparison doc: "~15").
    assert len(m.agreed) == 13
    # Each run missed ~4-5 of the other's major findings.
    assert len(m.only_a) == 4
    assert len(m.only_b) == 4
    # The JetStream-CAS direct contradiction (run-1 "ok" vs run-2 "bug").
    assert len(m.contradictions) == 1

    # Each run's headline finding is in the *other* run's blind spot.
    assert any(f.concern_key == "root-children-dead-field" for f in m.only_a)
    assert any(f.concern_key == "two-phase-candidate-closed" for f in m.only_b)

    # The number. Far below the proposed 0.75 / 0.90 bar — that's the point.
    assert round(m.jaccard(), 2) == 0.59  # 13 / 22
    assert round(m.jaccard(high_only=True), 2) == 0.45  # 5 / 11


def test_run0_strict_matcher_is_more_pessimistic() -> None:
    """The strict file+line+concern matcher scores *below* the human verdict
    because the two runs cited the same "no DLQ" concern at different files
    (run-1: jetstream/event_log.py; run-2: dispatcher.py). This gap is the
    Gate-1 matcher-sensitivity evidence — the cheap matcher is a lower bound."""
    run1 = ar.load_findings(FIXTURES / "run-1.findings.json")
    run2 = ar.load_findings(FIXTURES / "run-2.findings.json")
    m = ar.match_runs(run1, run2, require_file=True)

    assert len(m.agreed) == 12  # no-dlq drops out
    assert len(m.only_a) == 5
    assert len(m.only_b) == 5
    # no-dlq appears as a "miss" on *both* sides: same concern, different file.
    assert any(f.concern_key == "no-dlq" for f in m.only_a)
    assert any(f.concern_key == "no-dlq" for f in m.only_b)

    assert round(m.jaccard(), 2) == 0.52  # 12 / 23
    assert round(m.jaccard(high_only=True), 2) == 0.33  # 4 / 12

    # Both matchers agree on the conclusion: run-0 is far below any sane bar.
    assert m.jaccard() < 0.75
    assert m.jaccard(high_only=True) < 0.90


def test_score_runs_reports_median_over_pairs() -> None:
    run1 = ar.load_findings(FIXTURES / "run-1.findings.json")
    run2 = ar.load_findings(FIXTURES / "run-2.findings.json")
    report, matches = ar.score_runs([run1, run2], require_file=False)
    assert report.n_runs == 2
    assert report.finding_counts == [18, 18]
    assert len(report.pairwise) == 1
    assert round(report.median_all, 2) == 0.59
    # format smoke-test
    out = ar.format_report(report, matches, labels=["run-1", "run-2"])
    assert "FAIL" in out
    assert "CONTRADICTION" in out
