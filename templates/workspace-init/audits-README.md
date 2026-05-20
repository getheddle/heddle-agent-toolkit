# audits/

Persistent record of repository audits that seed maintenance cycles.

Each sibling repo listed in `.heddle-workspace.yaml` gets its own
subfolder: `<repo>-audits/`. The folder is created lazily by
`workspace init` / `workspace add` and stays even if a repo is later
removed from the manifest — audits are historical artifacts and
deletion is never automatic.

## Layout

```
audits/
  README.md                          (this file)
  <repo>-audits/
    .gitkeep
    <topic>-audit-<YYYY-MM-DD>.md    single-file audit
    <topic>-audit-<YYYY-MM-DD>/      multi-dimensional audit (folder)
      0-summary.md
      <facet>.md
      ...
```

Example:

```
audits/heddle-audits/contrib-events-audit-2026-05-19.md
audits/heddle-sdk-audits/deps-audit-2026-06-01/
  0-summary.md
  dotnet.md
  swift.md
```

## Naming convention

```
<topic>-audit-<YYYY-MM-DD>(.md | /)
```

- `<topic>` — lowercase kebab-case. Subject of the audit
  (`contrib-events`, `deps`, `security`, `schema-drift`, `docs`,
  `perf`).
- `<YYYY-MM-DD>` — the date the audit was performed. Bake it into the
  name; the audit is a frozen snapshot, not a living doc.
- `.md` for single-file; trailing `/` (with `0-summary.md`) for
  multi-dimensional.

## Audit → maintenance cycle linkage

Audits seed maintenance cycles. The link is **mechanical, by name**:

```
audit:  audits/<repo>-audits/<topic>-audit-<YYYY-MM-DD>(.md|/)
cycle:  session-starters/<repo>-<topic>-<YYYY-MM-DD>/
```

(Drop the `-audit-` infix in the cycle folder; the cycle isn't the
audit, it's the work the audit produced.)

The cycle subfolder follows the layout in
[`../session-starters/README.md`](../session-starters/README.md):
`0-roadmap-overview.md` plus lettered thematic sibling sessions
(`A-…md`, `B-…md`, …). The overview links back to its source audit by
relative path.

## Audit types

The catalog of supported audit types, what each one inspects, and the
default scope live in
[`../heddle-workspace/docs/AUDITS.md`](../heddle-workspace/docs/AUDITS.md).

The `audit-runner` subagent reads that doc to choose its lens; the
`maintenance-planner` subagent reads completed audits from here.

## What goes here vs. elsewhere

- **Here:** audit reports — read-only historical artifacts.
- **`../session-starters/<cycle>/`:** the executable work an audit
  produced.
- **Sibling repo `docs/`:** living architecture, not audits.
- **`../(experimental)/`:** ad-hoc explorations that aren't audits.
