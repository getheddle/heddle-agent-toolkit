# warp-design Documentation Audit

First-time-user audit performed 2026-05-15 against `warp-design/` as a
read-only review. Scope: README, VISION, EVOLUTION_LOG, AGENTS, CLAUDE,
`decisions/`, `exploration/`, `daemon-v0/`, `research/`.

## CRITICAL (broken or wrong, must fix)

- [research/README.md:13-17] Table lists five research files (`SWIFT_6.md`,
  `SERVER_ECOSYSTEM.md`, `APPLE_FRAMEWORKS.md`, `MCP_SWIFT.md`,
  `DISTRIBUTION.md`) all marked TODO — **none of these files exist** in
  `research/`. The directory contains only `README.md`. Per the repo's
  own "Conventions" section ("TODO files are committed empty-but-with-TOC
  so the gap is visible") they are supposed to exist as stubs. Every
  cross-reference to them is a dead link.
- [decisions/0002-language-swift-for-macos-agents.md:40] Links to
  `../research/SWIFT_6.md` — dead (see above).
- [decisions/0002-language-swift-for-macos-agents.md:96] Links to
  `../research/SERVER_ECOSYSTEM.md` — dead.
- [decisions/0002-language-swift-for-macos-agents.md:115-117] References
  `../research/SWIFT_6.md`, `../research/SERVER_ECOSYSTEM.md`,
  `../research/APPLE_FRAMEWORKS.md` — all dead.
- [daemon-v0/SCOPE.md:95] Links to `../research/MCP_SWIFT.md` — dead.
- [VISION_AD_HOC_CLUSTERS.md:3] Status declares "implementation
  underway via warp", but README.md:15-18 and `daemon-v0/SCOPE.md:2`
  both state pre-implementation/no production code yet. Direct
  contradiction — pick one truthful state.

## NOTABLE (will confuse new users, should fix)

- [README.md:69-73] Conventions list ADR sections as
  "Status, Context, Decision, Consequences." AGENTS.md:42-43 lists the
  authoritative format as "Status, Context, Decision, Consequences
  (Easier / Harder / Trade-offs accepted), References." README is
  missing both the Easier/Harder/Trade-offs sub-structure and
  References. Existing ADRs (0001–0004) follow the AGENTS.md format —
  README is the outlier.
- [README.md:70-71] ADR convention text omits the **Date** and
  **Deciders** front-matter fields, both of which all four existing
  ADRs include and which AGENTS.md's review checklist implicitly
  expects (ISO 8601 date check at line 82).
- [README.md:41-44] The relationship diagram labels the arrow from
  `heddle` to `warp-design` "implements vision from (referenced in
  heddle/docs/vision/)". The direction is confusing: heddle is the
  Python substrate, not the implementor of warp's vision — warp (the
  Swift repo, planned) is. The arrow from `warp-design` to `warp` is
  labeled "informs", which is right, but the upper arrow appears
  inverted or mis-labeled.
- [decisions/0003-warp-and-warp-design-repo-split.md:62-64] States
  "Use full GitHub URLs in cross-repo links; relative links only within
  a single repo." Yet CLAUDE.md and AGENTS.md (newly added) use
  relative paths like `../heddle-agent-toolkit/` for cross-repo
  references. These work on the local sibling-clone convention but
  violate the ADR's own guidance. Either revise the ADR or qualify the
  rule (it appears the convention has shifted to sibling-relative for
  toolkit anchors).
- [decisions/0002-language-swift-for-macos-agents.md:4-6] The Status
  field is "Accepted (for macOS only; Linux/Windows agent language is
  a separate decision, expected to land as Rust per the
  language-asymmetry preference established here)". This is a long
  parenthetical inside a Status value. The four allowed statuses
  (Proposed / Accepted / Deprecated / Superseded — implied by the
  repo's ADR style) should be one word. Move the qualification into
  Context or Decision.
- [decisions/0001-pursue-ad-hoc-cluster-orchestration.md:88] References
  "Original infographic + whiteboard artifacts (Hooman's local files;
  not redistributed in this repo for now)". For a first-time contributor
  this is a dead-end pointer — there's no way to retrieve or learn
  more. Either drop the reference, archive a redacted copy in repo, or
  link to a location where the artifacts live.
- [VISION_AD_HOC_CLUSTERS.md:183-194] "Open questions" list partially
  duplicates `daemon-v0/SCOPE.md:147-165`'s "Open architectural
  questions" list. Trust/admission and IPC protocol appear in both
  with slightly different phrasings. Pick one canonical home and
  cross-reference.
- [VISION_AD_HOC_CLUSTERS.md:185] Lists "License (likely Apache-2.0;
  ADR pending)" as open. README.md:91-94 says the same thing and
  references a future `decisions/000X-license.md`. There is no ADR for
  this — fine that it's open, but the inconsistent
  forward-reference placeholder (`000X`) is non-standard; either commit
  to `0005-license.md` or drop the bogus number.

## MINOR (polish, can defer)

- [README.md:94] Trailing parenthetical "(See
  `decisions/000X-license.md` when written.)" — placeholder
  filename should not appear in shipped docs; use prose instead.
- [decisions/0001-pursue-ad-hoc-cluster-orchestration.md:17] Refers
  to the conversation as "(see `../EVOLUTION_LOG.md`, 2026-04-29 Origin
  entry)". The log has three 2026-04-29 entries; specifying
  "Origin" is good but ensure the title in EVOLUTION_LOG.md
  (`## 2026-04-29 — Origin`) doesn't drift.
- [EVOLUTION_LOG.md:46] Heading "Triggering context: the TCC episode"
  is dated 2026-04-29 with prose "in the immediately preceding session"
  — this is fine for now, but the relative reference will rot. Anchor
  to a date or commit hash.
- [daemon-v0/SCOPE.md:45] "Read `~/.heddle/agent.yaml` (or rename — we'll
  bikeshed in v0)." — open question repeated at line 158-160. One
  mention is enough.
- [exploration/CLUSTER_ARCHITECTURE.md:5-7] Status "Exploration. Not
  committed. Captures the architectural shape discussed on 2026-04-29
  before serious research; expect this to evolve substantially…" is
  excellent first-time framing — consider mirroring this caveat style
  to `exploration/PRIOR_ART.md` whose Status line is briefer.
- [exploration/PRIOR_ART.md:3] "Snapshot as of 2026-04-29; landscape
  changes fast and this needs periodic refresh." — could add a
  "review by" date to make the staleness window explicit (e.g.
  "review by 2026-07").
- [VISION_AD_HOC_CLUSTERS.md:107] Final row in macOS-rationale table
  uses parenthetical "(Hooman)" — fine, but the same operator is
  referenced as "the initial implementer" elsewhere; consider
  consistent voice.
- [AGENTS.md:35] Lists `daemon-v0/SCOPE.md` — singular file. README.md:28
  describes the directory as "Spec for the immediate Swift daemon-core
  deliverable" (also singular). The `daemon-v0/` directory holds one
  file; fine, but it could be a sibling top-level `DAEMON_V0_SCOPE.md`
  unless additional files are planned. Tiny structural quibble.
- [decisions/0004-naming-warp.md:50] "Binary: `warp` (with `warp-agent`
  as a possible later rename if the unprefixed name causes friction in
  the wild)" — uses backtick formatting consistently here. Good model
  for other ADRs.

## DISCOVERABILITY GAPS

- **No index of ADRs by status.** A first-time reader landing in
  `decisions/` sees four numbered files but cannot tell at a glance
  which are Accepted, Proposed, Superseded. A `decisions/README.md` or
  index table at the bottom of the top-level README would solve this.
  All four current ADRs are Accepted, so today the gap is latent, but
  the moment a 0005-license-pending lands it becomes a real problem.
- **No "start here" reading order.** README lists what's in the repo
  but doesn't tell a first-time contributor the order to read things in
  (VISION → ADR 0001 → EVOLUTION_LOG → daemon-v0 SCOPE → exploration).
  AGENTS.md has a "Read first" section that does this for agents but
  not for humans.
- **The "design-only" framing is buried.** AGENTS.md leads with it
  ("no production code"), but README.md states it indirectly via
  "Production code lives in a separate repo (planned: `getheddle/warp`)"
  on line 8 of a multi-paragraph intro. A first-time visitor scanning
  the README could miss that this repo is intentionally code-free.
  Worth a one-line callout near the top, e.g. a `> Note:` banner.
- **Cross-repo invariant C7 is not visible from this repo.** It lives
  in `heddle-agent-toolkit/anchors/INVARIANTS.md`, mentioned in
  CLAUDE.md:18-21 and AGENTS.md:24-27. A first-time contributor
  writing an ADR without reading the toolkit could miss it. Consider
  a one-line restatement in the ADR template/format section of
  AGENTS.md ("ADRs that propose changes to heddle or heddle-sdk: scope
  the proposal, do not dictate PR shape — invariant C7").
- **No ADR template file.** The repo describes the format prose-only
  in README/AGENTS. A `decisions/TEMPLATE.md` (or `0000-template.md`)
  would make `cp template.md NNNN-new.md` trivial. The `/warp-adr`
  skill is referenced as the production path, but a static template
  helps anyone not using that skill.
- **`heddle/docs/vision/AD_HOC_CLUSTERS.md` divergence is mentioned
  but not surfaced.** README.md:63-65 says the warp-design copy "may
  run ahead" of heddle's canonical copy. There's no log or diff
  pointer showing which is currently ahead. For a first-time reader
  who reads both, the inconsistency could be confusing. Consider a
  "last sync: YYYY-MM-DD" stamp at the top of
  `VISION_AD_HOC_CLUSTERS.md`.
- **Research streams are listed but their priority order isn't
  obvious.** `research/README.md:31-37` describes "pick the
  highest-leverage stream" without saying which that is. The five
  stubs are listed in some order in the table but it's not declared
  to be a priority order. State the implementation-gating priority
  explicitly.
- **No glossary.** Terms like "warp threads", "BAFT", "heddle worker",
  "queue group", "NATS", "SMAppService", "TCC", "FDA" appear
  throughout; a first-time reader unfamiliar with the project will
  need to context-switch out. A short `GLOSSARY.md` (or section in
  README) would lower the entry tax.

## Recent-refactor leftovers (C7 check)

Scanned all four ADRs and exploration/research notes for language that
reads as implementation directives at `heddle` or `heddle-sdk`. **None
of the existing ADRs cross the line** — they describe warp's
architecture and explicitly defer to heddle's PR flow (ADR 0001:46
"implementation lives in a new repo `getheddle/warp`"). The closest
brushes:

- `VISION_AD_HOC_CLUSTERS.md:109-127` ("Why heddle is positioned to
  own this") describes what heddle's existing primitives map to in
  warp. This is mapping/observation, not directive — within C7.
- `exploration/CLUSTER_ARCHITECTURE.md:193-209` ("How heddle's existing
  pieces map") — same pattern, observational, fine.
- `daemon-v0/SCOPE.md:75-81` describes a UDS protocol the Swift daemon
  will use to talk to the Python subprocess. The protocol shape is
  declared here (JSON-NDJSON, version field). If the Python side has
  to implement matching protocol code, this ADR-equivalent doc is
  edging close to dictating heddle behavior. Recommend reframing as
  "warp v0 proposes a UDS protocol; heddle's adoption of the matching
  client lives in a heddle PR" to stay firmly on the propose side of
  C7.

No ADR currently violates C7, but the daemon-v0 IPC spec is the place
to watch as the design moves toward an actual heddle PR.
