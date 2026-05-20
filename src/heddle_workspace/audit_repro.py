"""Audit reproducibility scorer (Phase 0 of the audit-subsystem hardening).

Measures how reproducible a design audit is by scoring the *finding overlap*
across N independent runs of the same audit on the same code.

Why this exists
---------------
The 2026-05-19 reproducibility experiment showed two independent design audits
of the same unchanged `heddle.contrib.events` code agreed on a stable core of
~15 findings but each missed 4-5 major findings the other caught — including
each run's own headline finding. A single open-ended audit pass is not
reproducible enough to build a pipeline on. Before hardening the `audit-runner`
we need a *number*. This module is that number.

Separation of concerns (deliberate)
------------------------------------
- **Extraction** (audit prose -> normalized `Finding` list) is the subjective,
  model-driven step. It happens upstream: either the audit emits a
  machine-readable findings block (the Phase-0 prompt template requires this),
  or a human/agent extracts findings into JSON. This module does *not* parse
  free-form audit prose — that was the un-reproducible step we are measuring.
- **Scoring** (this module) is pure and deterministic: given the normalized
  finding lists, it computes pairwise Jaccard overlap and the symmetric
  differences. Deterministic input -> deterministic output, so it is unit
  testable and the harness around it can stay dumb.

The matcher is intentionally cheap (file + line-window + concern key). Whether a
semantic matcher is needed is a Gate-1 decision; see
`heddle-workspace/docs/AUDIT_REPRO.md`.
"""

from __future__ import annotations

import json
import re
import statistics
from dataclasses import dataclass, field
from itertools import combinations
from pathlib import Path

# Default line-number tolerance when matching two findings that cite the same
# file. Two runs rarely cite byte-identical line ranges for the same concern.
DEFAULT_LINE_WINDOW = 25


@dataclass(frozen=True)
class Finding:
    """One normalized audit finding.

    `concern_key` is the load-bearing field for matching: a short, stable slug
    naming *what* is wrong (e.g. `jetstream-cas`, `p3-restart-timer-loss`).
    Two runs that independently spotted the same issue must be given the same
    `concern_key` during extraction for them to match — which is exactly why
    extraction reproducibility is the open question, not scoring.

    `stance` lets the scorer catch the case where both runs examined the same
    spot but reached *opposite* conclusions (the run-0 JetStream-CAS
    contradiction). Default `"finding"` means "this is a real problem". A run
    that gave the same spot a clean bill of health records `stance="ok"`.
    """

    concern_key: str
    file: str
    line: int | None = None
    severity: str = "medium"  # low | medium | high
    stance: str = "finding"  # finding | ok
    summary: str = ""

    @property
    def is_high(self) -> bool:
        return self.severity.lower() == "high"


@dataclass
class MatchResult:
    """Outcome of comparing two runs' finding lists."""

    agreed: list[tuple[Finding, Finding]] = field(default_factory=list)
    only_a: list[Finding] = field(default_factory=list)
    only_b: list[Finding] = field(default_factory=list)
    # Same location + concern, opposite stance (a real divergence masquerading
    # as agreement). Not counted as agreement.
    contradictions: list[tuple[Finding, Finding]] = field(default_factory=list)

    def jaccard(self, *, high_only: bool = False) -> float:
        """|intersection| / |union| over findings.

        Contradictions count toward the union (they are two findings that do
        *not* agree) but never toward the intersection.
        """

        def keep(f: Finding) -> bool:
            return f.is_high if high_only else True

        agreed = [p for p in self.agreed if keep(p[0]) or keep(p[1])]
        only_a = [f for f in self.only_a if keep(f)]
        only_b = [f for f in self.only_b if keep(f)]
        contra = [p for p in self.contradictions if keep(p[0]) or keep(p[1])]

        intersection = len(agreed)
        union = intersection + len(only_a) + len(only_b) + len(contra)
        if union == 0:
            return 1.0  # vacuously identical: nothing to disagree about
        return intersection / union


def _normalize_concern(key: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", key.strip().lower()).strip("-")


def _lines_match(a: int | None, b: int | None, window: int) -> bool:
    """Line numbers match if both absent, or within `window` of each other.

    A finding with no line is matched on file + concern alone (some findings
    are module-wide, not line-anchored).
    """
    if a is None or b is None:
        return True
    return abs(a - b) <= window


def match_runs(
    run_a: list[Finding],
    run_b: list[Finding],
    *,
    line_window: int = DEFAULT_LINE_WINDOW,
    require_file: bool = True,
) -> MatchResult:
    """Greedily match findings between two runs.

    Concern key must always match (after normalization). `require_file` controls
    strictness — the Gate-1 matcher question made concrete:

    - `require_file=True` (strict, default): also require same `file` and line
      numbers within `line_window`. Pessimistic: two runs that flagged the same
      concern at different files (e.g. run-0's "no DLQ" cited at the event log
      by one run, at the dispatcher by the other) score as a *miss*.
    - `require_file=False` (concern-only): match on concern key alone, closer to
      a human's semantic match. Risks conflating two distinct problems that got
      the same key.

    Among candidates, the closest line wins. Matched pairs with opposite
    `stance` are recorded as contradictions, not agreements.
    """
    result = MatchResult()
    unmatched_b = list(range(len(run_b)))

    for fa in run_a:
        best_j: int | None = None
        # Tie-break only: among accepted candidates, prefer the closest line.
        # Acceptance (concern / file / line-window) is filtered below; this is
        # not itself a filter, so it starts unbounded.
        best_dist = float("inf")
        for j in unmatched_b:
            fb = run_b[j]
            if _normalize_concern(fa.concern_key) != _normalize_concern(fb.concern_key):
                continue
            if require_file:
                if Path(fa.file).as_posix() != Path(fb.file).as_posix():
                    continue
                if not _lines_match(fa.line, fb.line, line_window):
                    continue
            dist = (
                abs((fa.line or 0) - (fb.line or 0))
                if fa.line is not None and fb.line is not None
                else 0
            )
            if dist < best_dist:
                best_dist = dist
                best_j = j
        if best_j is None:
            result.only_a.append(fa)
        else:
            fb = run_b[best_j]
            unmatched_b.remove(best_j)
            if fa.stance != fb.stance:
                result.contradictions.append((fa, fb))
            else:
                result.agreed.append((fa, fb))

    result.only_b = [run_b[j] for j in unmatched_b]
    return result


@dataclass
class ReproReport:
    """Aggregate reproducibility over N runs (all pairwise comparisons)."""

    n_runs: int
    finding_counts: list[int]
    pairwise: list[tuple[int, int, float, float]]  # (i, j, jaccard_all, jaccard_high)

    @property
    def median_all(self) -> float:
        return statistics.median(p[2] for p in self.pairwise) if self.pairwise else 1.0

    @property
    def median_high(self) -> float:
        return statistics.median(p[3] for p in self.pairwise) if self.pairwise else 1.0

    @property
    def spread_all(self) -> tuple[float, float]:
        vals = [p[2] for p in self.pairwise]
        return (min(vals), max(vals)) if vals else (1.0, 1.0)


def score_runs(
    runs: list[list[Finding]],
    *,
    line_window: int = DEFAULT_LINE_WINDOW,
    require_file: bool = True,
) -> tuple[ReproReport, list[tuple[int, int, MatchResult]]]:
    """Score N>=2 runs. Returns the aggregate report and every pairwise match."""
    if len(runs) < 2:
        raise ValueError("need at least 2 runs to measure reproducibility")
    pairwise: list[tuple[int, int, float, float]] = []
    matches: list[tuple[int, int, MatchResult]] = []
    for i, j in combinations(range(len(runs)), 2):
        m = match_runs(
            runs[i], runs[j], line_window=line_window, require_file=require_file
        )
        pairwise.append((i, j, m.jaccard(), m.jaccard(high_only=True)))
        matches.append((i, j, m))
    report = ReproReport(
        n_runs=len(runs),
        finding_counts=[len(r) for r in runs],
        pairwise=pairwise,
    )
    return report, matches


# --------------------------------------------------------------------------
# Ingestion
# --------------------------------------------------------------------------

_FINDINGS_BLOCK = re.compile(
    r"```(?:json\s+)?findings\s*\n(.*?)\n```",
    re.DOTALL | re.IGNORECASE,
)


def _findings_from_records(records: list[dict]) -> list[Finding]:
    out: list[Finding] = []
    for r in records:
        out.append(
            Finding(
                concern_key=r["concern_key"],
                file=r["file"],
                line=r.get("line"),
                severity=r.get("severity", "medium"),
                stance=r.get("stance", "finding"),
                summary=r.get("summary", ""),
            )
        )
    return out


def load_findings(path: Path) -> list[Finding]:
    """Load findings from a `.json` array, or from a ```findings block embedded
    in a Markdown audit report.

    A real audit run (Phase 0 prompt template) embeds a fenced ```findings JSON
    block in its report; this reads that block back. A `.json` file (the run-0
    fixtures) is read directly.
    """
    text = path.read_text()
    if path.suffix == ".json":
        return _findings_from_records(json.loads(text))
    m = _FINDINGS_BLOCK.search(text)
    if not m:
        raise ValueError(
            f"{path}: no ```findings JSON block found. The audit must emit one "
            "(see heddle-workspace/docs/AUDIT_REPRO.md)."
        )
    return _findings_from_records(json.loads(m.group(1)))


# --------------------------------------------------------------------------
# Reporting
# --------------------------------------------------------------------------


def format_report(
    report: ReproReport,
    matches: list[tuple[int, int, MatchResult]],
    *,
    labels: list[str] | None = None,
    bar_high: float = 0.90,
    bar_all: float = 0.75,
) -> str:
    labels = labels or [f"run-{i}" for i in range(report.n_runs)]
    lines: list[str] = []
    lines.append(f"Reproducibility over N={report.n_runs} runs")
    lines.append("=" * 48)
    for i, lab in enumerate(labels):
        lines.append(f"  {lab}: {report.finding_counts[i]} findings")
    lines.append("")
    lines.append("Pairwise Jaccard (all / high-severity):")
    for i, j, jall, jhigh in report.pairwise:
        lines.append(f"  {labels[i]} vs {labels[j]}: {jall:.2f} / {jhigh:.2f}")
    lo, hi = report.spread_all
    lines.append("")
    lines.append(
        f"MEDIAN: all={report.median_all:.2f}  high={report.median_high:.2f}  "
        f"(all spread {lo:.2f}-{hi:.2f})"
    )
    bar_all_ok = "PASS" if report.median_all >= bar_all else "FAIL"
    bar_high_ok = "PASS" if report.median_high >= bar_high else "FAIL"
    lines.append(
        f"BAR:    all>={bar_all:.0%} [{bar_all_ok}]  high>={bar_high:.0%} [{bar_high_ok}]"
    )

    # Per-pair symmetric difference so misses are inspectable.
    for i, j, m in matches:
        if not (m.only_a or m.only_b or m.contradictions):
            continue
        lines.append("")
        lines.append(f"-- {labels[i]} vs {labels[j]}: divergences --")
        for f in m.only_a:
            lines.append(
                f"  only {labels[i]} [{f.severity}] {f.concern_key} ({f.file}:{f.line})"
            )
        for f in m.only_b:
            lines.append(
                f"  only {labels[j]} [{f.severity}] {f.concern_key} ({f.file}:{f.line})"
            )
        for fa, fb in m.contradictions:
            lines.append(
                f"  CONTRADICTION {fa.concern_key} "
                f"({fa.file}:{fa.line}): {labels[i]}={fa.stance} vs "
                f"{labels[j]}={fb.stance}"
            )
    return "\n".join(lines)


def run(args) -> int:
    """CLI entry: `workspace audit-repro score <findings...>`."""
    paths = [Path(p) for p in args.findings]
    runs = [load_findings(p) for p in paths]
    labels = [p.stem for p in paths]
    report, matches = score_runs(
        runs,
        line_window=args.line_window,
        require_file=not args.concern_only,
    )
    print(format_report(report, matches, labels=labels))
    return 0
