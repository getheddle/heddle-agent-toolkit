# audits/

Historical documentation audits produced by AI agents during the
toolkit's initial buildout. These are snapshots — not canonical toolkit
content. Each file captures what was true on the date it was written;
the underlying repos have moved on.

## Contents

| File | Date | Repo audited | What it found |
|---|---|---|---|
| `audit-heddle.md` | 2026-05-15 | `heddle/` | 0 broken in-repo links; 3 critical (stale CLAUDE.md refs after split, `pip install heddle` instead of `heddle-ai`); ~12 notable. |
| `audit-heddle-sdk.md` | 2026-05-15 | `heddle-sdk/` | 2 critical (broken SwiftPM snippets in NATS.md and SWIFT.md); ~6 notable; cross-repo coherence flag that caught the toolkit's own `{goal_id}` → `{parent_task_id}` bug. |
| `audit-warp-design.md` | 2026-05-15 | `warp-design/` | 6 critical (missing research stubs + VISION/README status contradiction); ~7 notable. C7 compliance clean. |

## Why keep these

These audits triaged the documentation cleanup that accompanied the
toolkit's introduction. Many findings were fixed in the same session
("Bundle scope" in the planning log); some were deferred to dedicated
sessions; some were judgment calls deferred to the user.

Keeping the audits makes the *decisions* legible: a future contributor
can see what was flagged, what was bundled, what was deferred, and
why — rather than trying to reverse-engineer it from the diff history.

## When to rerun

A fresh-eyes audit pays off when:

- A major documentation refactor lands across multiple repos.
- A new sibling repo joins the family (e.g., `warp` when it ships).
- The toolkit's anchor docs are restructured.
- Doc rot complaints from users accumulate.

The `general-purpose` Claude Code subagent can do another pass with a
prompt similar to the ones used here. Write findings into a new file
in this directory dated with the audit day.
