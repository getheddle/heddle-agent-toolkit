# Heddle Documentation Audit — First-Time-User Pass

Auditor: read-only sweep, 2026-05-15. Scope: markdown sources in
`/Volumes/Data/Developer/IranTransitionProject/heddle/`. Excludes the
built `site/` directory and the two `REPOSITORY_REVIEW_*.md` archival
files (those are historical reviews, not user-facing).

A scripted relative-link scan across `README.md`, `AGENTS.md`,
`CLAUDE.md`, `GOVERNANCE.md`, `FEEDBACK.md`, `docs/**.md`, and
`examples/*/README.md` returned **0 broken in-repo links**. All
referenced files exist. All CLI commands in `docs/CLI_REFERENCE.md`
match `src/heddle/cli/`. All shipped workers in
`docs/workers-reference.md` resolve to `configs/workers/`. All extras
named in `docs/GETTING_STARTED.md` exist in `pyproject.toml`.

The issues below are about accuracy of prose, post-refactor leftovers,
and first-time-user friction — not link rot.

---

## CRITICAL (broken or wrong, must fix)

- `README.md:240-243` — Says `CLAUDE.md` "documents the architecture
  and design rules for AI-assisted sessions." That description was true
  before the split. CLAUDE.md is now a 35-line pointer to AGENTS.md +
  the toolkit. The architecture/design content lives in AGENTS.md and
  `../heddle-agent-toolkit/anchors/`. New users following this lead
  will land on a stub.
- `docs/CONTRIBUTING.md:129-131` — Same stale claim: "The `CLAUDE.md`
  file documents the project's architecture, design rules, and current
  state for AI-assisted sessions." Same fix needed; should point to
  `AGENTS.md` (this repo) and the toolkit.
- `examples/town-hall/README.md:25`, `examples/debate-arena/README.md:31`,
  `examples/blind-taste-test/README.md:52` — Install command uses
  `pip install heddle[council]` / `pip install heddle[council,chatbridge]`.
  Package name on PyPI per `pyproject.toml` is `heddle-ai`, not
  `heddle`. Every other doc (README, GETTING_STARTED, index, council-
  howto, LOCAL_DEPLOYMENT, building-workflows, workshop, rag) uses
  `pip install heddle-ai[...]`. A clean-machine user copy-pasting
  these three commands will get either "no matching distribution" or
  the wrong package.

## NOTABLE (will confuse new users, should fix)

- `AGENTS.md:97` — "MCP gateway: `docs/building-workflows.md` Part 11."
  The MCP gateway is **Part 12** in that file; Part 11 is "DuckDB
  integration". Stale section number.
- `GOVERNANCE.md:27` — Founder email is `hooman@mac.com`; everywhere
  else (README, CONTRIBUTING, GOVERNANCE.md line 5) the contact is
  `admin@getheddle.dev`. Looks like a placeholder that survived. A
  first-time user reading governance will reasonably distrust the
  inconsistency.
- `docs/CONTRIBUTING.md:9` — Links GOVERNANCE.md via an absolute
  GitHub URL (`https://github.com/getheddle/heddle/blob/main/GOVERNANCE.md`)
  instead of a relative path. Mkdocs Material doesn't render that as
  an in-site link; new users browsing the published site get an
  off-site bounce when an in-repo link would do.
- `README.md` "Documentation" section (lines 172-208) — does **not**
  link to `docs/BLIND_AUDIT.md`, even though that doc is named in
  Key Features ("Knowledge Silos") and is linked from `docs/index.md`.
  Users hitting the README first never find the blind-audit guide.
- `README.md:201` and `mkdocs.yml:94` — Both link to
  `https://getheddle.github.io/heddle-sdk/` for the SDK docs. The
  Heddle SDK and Workshop screens claim that page exists; if the
  `heddle-sdk` Pages site isn't yet published this is a dead link from
  a first-time-user perspective. Worth verifying before next release.
- `docs/index.md:113` (and `docs/GETTING_STARTED.md:113-119` worker
  table) — The README table claims `extractor` is `local` tier and
  the Getting Started table says `extractor` is `standard` tier. The
  reference doc says... need a single source of truth. (Cross-checked:
  the Getting Started table at line 113-119 lists `extractor` as
  `standard`; the README's "Have Telegram exports?" paragraph and
  several other places imply all six work on `local`.) Reconcile in
  one direction.
- `README.md:223` and `AGENTS.md:50` disagree on test coverage:
  README says "91%+ coverage", AGENTS.md says "90%+ coverage". Not
  fatal but obvious to anyone scanning both files.
- `docs/api/contrib.md` table (lines 7-14) — Missing `contrib.subprocess`,
  which exists in `src/heddle/contrib/subprocess/` and is named in
  `AGENTS.md:48`. New users grepping the API reference for the
  subprocess processor pattern won't find it.
- `docs/CONCEPTS.md:108` ("Direct mode (no infrastructure)") — Says
  `heddle setup` "detects Ollama, sets paths." Every other doc says
  the wizard auto-detects **both LM Studio and Ollama** (and LM
  Studio wins when both are present). Mentioning only Ollama in
  Concepts is stale — likely predates the LM-Studio-first change
  flagged in AGENTS.md:56-57.
- `docs/index.md` "Documentation → Go deeper" lists
  `[Adversarial Review](BLIND_AUDIT.md)` but the parallel section in
  `README.md` does not. Inconsistent advertised entry points between
  the two top-level landing pages.
- `docs/GETTING_STARTED.md:147` — "uv" listed under prerequisites as
  *recommended for development* but the very first command in the
  Quick Start (lines 14-23) is `pip install heddle-ai[workshop]`.
  Step 1 of the "Prerequisites (Full Infrastructure)" section
  (line 155, `uv sync --all-extras`) then assumes uv is already
  installed without saying how to install it (other than the link).
  A clean-machine reader who didn't install uv will hit
  `uv: command not found` between sections 1 and 2.
- `docs/GETTING_STARTED.md:230-247` — Tells users to `brew install
  nats-server valkey` or run Docker. No mention of Linux/Windows
  alternatives. The "Prerequisites" block above never declared macOS
  as an OS assumption. The Docker fallback is there, but the brew
  command is presented as the default.
- `docs/index.md:38` and `README.md:26` — Both say "open the web UI at
  localhost:8080" but `docs/SECURITY_MODEL.md:29` documents the default
  bind as `127.0.0.1`. That's fine in practice, but new users reading
  the security model will wonder why every other page says "localhost"
  if loopback enforcement is a posture decision. Minor wording
  reconciliation.
- `docs/api/contrib.md:13` — RAG row is described as "Social media
  stream RAG pipeline". The `rag-howto.md`, README, and Getting
  Started have already broadened RAG ingestion to CSV and plain text
  (per `FEEDBACK.md` v0.9.2 changelog). The "social media" framing is
  narrow and outdated.

## MINOR (polish, can defer)

- `README.md:10` (HTML comment) — "Keep in sync with pyproject.toml
  version" — useful note, no action.
- `docs/adr/index.md:37` — ADR-006 "pairs with" lists commit
  `15a9af4` rather than an invariant. Inconsistent style across the
  table but not wrong.
- `docs/BLIND_AUDIT.md:400-401` — "Application Patterns (patterns 1-10
  cover this material)" — this prose was flagged stale in
  `REPOSITORY_REVIEW_2026-05-10.md:130`. Worth checking if
  `docs/APPLICATION_PATTERNS.md` actually contains numbered
  patterns 1-10 today.
- `docs/CLI_REFERENCE.md` overview table lists 22 distinct commands
  (counting groups + subs); `FEEDBACK.md` mentions an earlier
  "All 17 commands" wording. Worth a quick verification that README
  / index don't still cite an old count somewhere — currently I
  found no surviving "17 commands" string, so this is just a
  watch-item.
- `examples/document-intake/README.md:49` and parallel research-review
  step — "Also ensure the processing module is importable (see
  tutorial)" leaves the user one indirection away from a concrete
  step. Could inline the `PYTHONPATH` hint.
- `docs/CONCEPTS.md:103-113` — Example commands use `uv run heddle
  setup` then `uv run heddle rag ingest`. Every other Quick Start
  uses bare `heddle setup`. Two valid styles, but a first-time user
  going CONCEPTS → GETTING_STARTED will see them flip.
- `docs/GETTING_STARTED.md:282` — `brew tap nats-io/nats-tools && brew
  install nats-io/nats-tools/nats` is correct but verbose; the
  `nats-cli` formula is now in the default tap.
- `docs/rag-howto.md:605-608` — References `examples/rag_demo.py`,
  which exists. Fine. Note: this is the only example **not** under
  its own subdirectory with a README; minor inconsistency with the
  other five examples that have `examples/<name>/README.md`.
- `FEEDBACK.md` — A session report from 2026-04-26 → 2026-04-27 that
  mentions "Heddle v0.9.1 → 0.9.2". It's archival but lives at the
  repo root next to `README.md`/`GOVERNANCE.md`, so a first-time
  user file-listing sees it. Consider moving to `(archive)/` or a
  `docs/sessions/` folder. Same applies to `RELEASE_NOTES_v0.9.2.md`
  at root.

## DISCOVERABILITY GAPS

- **No mention of AGENTS.md anywhere in user-facing docs.** The
  AGENTS.md split is brand new and intentional, but every
  contributor-facing doc still talks about CLAUDE.md as the AI-
  assisted-development entry point. `docs/CONTRIBUTING.md`,
  `README.md`'s "AI-Assisted Development" section, and (arguably)
  the GitHub repo description should now name AGENTS.md as the
  canonical agent file and CLAUDE.md as the Claude-specific note.
- **No mention of `../heddle-agent-toolkit/` outside AGENTS.md and
  CLAUDE.md.** The toolkit is the new shared spine of cross-repo
  guidance, but a new contributor lands in `docs/CONTRIBUTING.md`
  and is never told it exists. At minimum, CONTRIBUTING should say
  "for cross-repo invariants, philosophy, and the wire-protocol
  contract, see `../heddle-agent-toolkit/anchors/`".
- **README ↔ docs/index.md drift.** These two files are 80%
  duplicates with subtle disagreements (BLIND_AUDIT link present in
  one, absent in the other; Workshop tier per worker; "Telegram
  exports?" wording). Maintaining both by hand is the bug; consider
  picking one as source and including the other.
- **`docs/CODING_GUIDE.md` is the project style guide but is not
  linked from `docs/CONTRIBUTING.md` until step 6 of "Pull Request
  Process".** It deserves a "Required reading before your first PR"
  link at the top.
- **No top-level "How to read this documentation" guide.** Heddle
  has Concepts, Why Heddle, Getting Started, Workshop Tour, three
  How-Tos, two Tutorials, two example sets, six runbooks, eight API
  pages, twelve ADRs, three application docs, and a security model.
  That's a lot of doors. A two-paragraph "If you're trying to X,
  read Y" cheat-sheet at the top of `docs/index.md` would compress
  the cognitive load.
- **Tutorial → example linkage is one-way.** Tutorials link to
  examples; example READMEs link back to tutorials. Good. But
  neither the README nor `docs/index.md` "Tutorials" rows tell the
  user that there's a runnable repo alongside the tutorial — so a
  reader who lands on the tutorial first might re-create files from
  scratch.
- **OS prerequisites are implicit.** `heddle setup` calls out
  Apple-Silicon MLX for LM Studio (`docs/GETTING_STARTED.md:192`),
  uses `brew` for nats/valkey, and the developer-workflow SVG
  diagram only exists for light/dark mode — no OS notes. Linux and
  Windows users are first-class but undeclared. A one-line "Tested
  on macOS and Linux; Windows via WSL recommended" up front would
  remove the guesswork.
- **`heddle-architect` / `heddle-invariant-guard` / `/heddle-orient`
  / `/heddle-preflight` are named in AGENTS.md and CLAUDE.md as
  subagents/skills, but the references assume the toolkit is
  already installed.** New contributors cloning fresh won't have
  `.claude/` populated. AGENTS.md should mention the
  `heddle-agent-toolkit/install.sh` step (or link to the toolkit's
  README) before naming the skills.

---

*End of audit. No files modified.*
