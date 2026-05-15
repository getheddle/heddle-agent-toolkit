---
name: warp-adr
description: Write or format an Architecture Decision Record in warp-design/decisions/ following the established NNNN-kebab-case-title.md format with Status/Context/Decision/Consequences sections. Use when the user wants to record a design decision for warp, propose a change that affects heddle or heddle-sdk from the design-repo side, or audit existing ADRs for format compliance.
---

# /warp-adr — write or check a warp-design ADR

Architecture Decision Records in `warp-design/decisions/` follow a fixed
format. This skill produces an ADR that matches the existing ones (see
`0001-pursue-ad-hoc-cluster-orchestration.md` and following).

## Filename

```
decisions/NNNN-kebab-case-title.md
```

- `NNNN` — zero-padded sequence number, next free integer. Run
  `ls warp-design/decisions/` to find the highest existing number; use
  the next one.
- Title — kebab-case, descriptive, concise. The filename title
  duplicates the `# NNNN. <title sentence>` heading inside.

## Required sections (in order)

```markdown
# NNNN. <One-sentence title>

- **Date:** YYYY-MM-DD
- **Status:** Proposed | Accepted | Superseded by [NNNN](NNNN-...md) | Rejected
- **Deciders:** <names / roles>

## Context

<What problem are we solving? What facts are on the ground? What
constraints apply? Cite EVOLUTION_LOG.md entries or other ADRs by link
when relevant. Keep this section dense — every sentence earns its place.>

## Decision

<What did we actually pick? State it crisply. If alternatives are
worth recording, summarize them at the end of this section under
"Alternatives considered" with one line each.>

## Consequences

**Easier**

- <what becomes simpler / unlocked>

**Harder**

- <what becomes more complex / what we now have to manage>

**Trade-offs accepted**

- <what we're choosing to live with that isn't ideal>

## References

- <Links to EVOLUTION_LOG.md, related ADRs, vision docs, external
  prior art that shaped the call.>
```

## Tone and content rules

- **Date in absolute ISO 8601.** "2026-05-15", not "yesterday."
- **Past tense for decisions already made; present tense for proposals.**
- **No marketing voice.** This is an internal record of reasoning.
- **Honest consequences.** The "Harder" and "Trade-offs accepted"
  sections are required, not optional. A consequence-free decision is a
  red flag — it usually means the trade-offs weren't surfaced.
- **Link laterally.** Reference related ADRs, the
  `VISION_AD_HOC_CLUSTERS.md` doc, and `EVOLUTION_LOG.md` entries where
  relevant. ADRs are nodes in a graph, not isolated essays.
- **No prescriptive implementation.** ADRs decide *direction*, not
  *implementation*. Code-level detail belongs in the upstream PR.

## When the ADR proposes a change to heddle or heddle-sdk

Invariant C7 (cross-repo invariants): warp-design ADRs may *propose*
changes to `heddle` or `heddle-sdk`. They do not *implement* those
changes. After the ADR is Accepted:

1. Open a PR (or discussion) in the relevant upstream repo
   referencing this ADR.
2. The implementation lands via that repo's normal flow.
3. When merged, update this ADR's References section with the PR link.

## After writing

Verify:

```bash
# Filename format
ls warp-design/decisions/ | grep '^[0-9]\{4\}-[a-z0-9-]\+\.md$' \
    || echo "FORMAT VIOLATION"

# Required sections present
grep -E '^## (Context|Decision|Consequences|References)$' \
    warp-design/decisions/NNNN-*.md
```

Then commit with a message that references the ADR number:
`docs(adr): NNNN — <short title>`.

## Auditing existing ADRs

If asked to audit, check each file in `decisions/`:

- Filename matches `NNNN-kebab-case-title.md`.
- First line is `# NNNN. <title>`.
- Has Date, Status, Deciders.
- Has Context, Decision, Consequences (with Easier / Harder / Trade-offs).
- Has References (may be empty list but the section is present).
- Status is one of the four allowed values.
- Date is ISO 8601.

Output a short report: `NNNN-title.md: OK` or `NNNN-title.md: <issue>`.
