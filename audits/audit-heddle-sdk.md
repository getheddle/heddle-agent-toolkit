# heddle-sdk documentation audit

First-time-user audit of markdown sources under `/Volumes/Data/Developer/IranTransitionProject/heddle-sdk`.
Scope: README.md, AGENTS.md, CLAUDE.md, all `docs/*.md`, and `examples/README.md`.
(No per-example READMEs exist — see Discoverability Gaps.)

## CRITICAL (broken or wrong, must fix)

- [docs/NATS.md:75] Swift `.product(...)` snippet is wrong:
  `\.product(name: "HeddleActorNATS", package: "HeddleActorNATS")`.
  When consuming via the SwiftPM dependency declared in the snippet
  immediately above (`.package(path: "../../swift-nats")`), the `package:`
  identifier is the directory name `swift-nats`, not `HeddleActorNATS`.
  And when consuming via the Git URL described in
  `docs/PUBLISHING.md:77` and `docs/SWIFT.md:19-22`, the package identity
  is the repo slug `heddle-sdk` (root manifest is `HeddleSDK` but SwiftPM
  resolves the identity from the URL). As written, a first-time Swift user
  copying this snippet will get a "no such package" error.

- [docs/SWIFT.md:25-28] The product-import snippet
  `.product(name: "HeddleActor", package: "heddle-sdk")` is inconsistent
  with the `dependencies` block four lines earlier
  (`.package(path: "../../swift")`). For the local-path case the `package:`
  should be `swift` (matching `examples/swift/echo-worker/Package.swift:23`
  which does exactly that). For the Git-URL case `heddle-sdk` is correct.
  Either split into two snippets or pick one consumption mode and stick
  with it — currently the page mixes both and neither works as a single
  copy/paste.

## NOTABLE (will confuse new users, should fix)

- [docs/CONCEPTS.md:35-40] Subjects table omits two subjects that the
  SDK's own `Subjects.cs` exposes as constants:
  `heddle.goals.incoming` (`IncomingGoals`) and the queue-group
  reference for `processors-{worker_type}`. The toolkit anchor
  `CONTRACT_MAP.md` lists `heddle.goals.incoming`. A reader of CONCEPTS
  will assume goals are out of scope.

- [docs/EXAMPLES.md:43-64] "Worker config in Heddle" YAML block uses
  `default_model_tier: local` and `implementation.runtime: swift`. The
  reader has no way to know whether these are real Heddle config keys
  or illustrative. There is no link to the canonical worker-config
  reference in upstream heddle. First-time users will copy this verbatim
  and hit "informational today" only by reading line 66. Either link to
  upstream's worker-config docs or flag the block as illustrative.

- [docs/CONTRIBUTING.md:8-10] Three bare absolute links to
  `getheddle/heddle/blob/main/*` (GOVERNANCE.md, DESIGN_INVARIANTS.md,
  foreign-actors.md). The recent AGENTS.md refactor pushed
  invariants/philosophy/contract-map into `heddle-agent-toolkit/anchors/`.
  CONTRIBUTING.md should at least mention the toolkit anchors as the
  first stop for contributors. Today AGENTS.md says "read those before
  structural work" but the contributor-facing doc never points there.

- [docs/ARCHITECTURE.md:96-97] Bare path references (not links) to
  `getheddle/heddle/docs/foreign-actors.md` and
  `getheddle/heddle/docs/DESIGN_INVARIANTS.md`. Make them clickable URLs
  matching the style used in `docs/CONTRIBUTING.md:8-10` (or, better,
  redirect to toolkit anchors for DESIGN_INVARIANTS-equivalents).

- [docs/SWIFT.md:18-22] Git-URL dependency uses `branch: "main"`. For a
  package not yet published this is fine, but `docs/PUBLISHING.md:77`
  uses `from: "0.1.0"`. The two docs disagree on the recommended
  consumption form. Pick one and cross-link to the other.

- [README.md:53-65] README's Documentation table omits
  `EXAMPLES.md` and `CODING_GUIDE.md`, both of which `docs/index.md`
  lists in its documentation map (lines 55 and 62). A first-time user
  exploring from GitHub sees fewer doc entries than a user landing on
  the rendered MkDocs site. Add the two rows.

- [docs/EXAMPLES.md:64] `implementation.runtime: swift` followed by
  `entry: ./bin/EchoWorker` — `./bin/EchoWorker` is the .NET output
  path, not a Swift binary location (`swift build` puts outputs under
  `.build/`). The example mixes languages confusingly. Either drop
  `entry` or split into language-specific blocks.

## MINOR (polish, can defer)

- [docs/index.md:55] vs [README.md table] — README is missing the
  Examples and Coding Guide rows (covered above).

- [docs/CONCEPTS.md:38] `heddle.results.default` is shown on a separate
  table row from `heddle.results.{parent_task_id}`. README.md:100
  collapses them as `heddle.results.{parent_task_id or "default"}`,
  which matches upstream `foreign-actors.md` and the SDK code path.
  Pick one form and use it consistently across CONCEPTS, NATS, WORKSHOP,
  PORTING (currently mixed).

- [docs/CODING_GUIDE.md:55-79] The `swift-nats` C++ headers workaround
  is duplicated almost verbatim in `docs/PUBLISHING.md:38-42`. Hoist
  into one place and cross-link.

- [docs/PORTING.md:46-49] Mentions `_trace_context` is "not yet in the
  exported schemas". `docs/CONTRACT_EVOLUTION.md:64-73` says the same
  thing. ROADMAP.md:163 lists it as an open decision. Three places now
  describe the same compatibility-sensitive extension — risk of drift.
  Centralize in CONTRACT_EVOLUTION and have PORTING/ROADMAP point at it.

- [docs/WORKSHOP.md:21] "Linux Swift workers should stay in-memory
  until upstream `nats-io/nats.swift` publishes Linux support" — same
  caveat appears verbatim in NATS.md:88-91, ARCHITECTURE.md:87-90,
  index.md:26-27, ROADMAP.md:30, PUBLISHING.md:94-97, README.md:25-27.
  Six restatements. Pick one canonical home (NATS.md is the obvious
  fit) and have the rest say "see NATS Transports for current status."

- [docs/EXAMPLES.md:33] Capitalization: "Use a shared broker transport,
  usually NATS. The shipped .NET NATS adapter is live-runtime ready;
  the shipped Swift NATS adapter builds the real binding on macOS."
  This sentence is also restated nearly verbatim in NATS.md and
  WORKSHOP.md (cf. previous bullet).

- [docs/CONTRIBUTING.md:32-46] PR checklist is identical to AGENTS.md's
  "Verification commands" (AGENTS.md:43-55) but with one extra
  `dotnet pack` line. Either merge or have one point at the other so
  they don't drift.

- [examples/README.md:39-40] Says "in-memory transport for a worker
  that needs to talk to a running Heddle or Workshop process" but the
  phrasing is awkward — "what not to copy: the in-memory transport"
  reads as a contradiction with the run instructions above. Rephrase
  as "swap to a broker transport when going cross-process."

- [docs/diagrams/README.md] Excluded from MkDocs nav via
  `mkdocs.yml:45 exclude_docs`, fine. No issue, just noting.

## DISCOVERABILITY GAPS

- **No per-example READMEs.** `examples/dotnet/EchoWorker/` and
  `examples/swift/echo-worker/` have no README. The audit prompt
  expected them. A foreign-language dev who clones the repo and
  `cd`s into the example will have no in-place context — they must
  jump back to `docs/EXAMPLES.md` or `docs/{SWIFT,DOTNET}.md`. Add a
  10-line per-example README pointing back to the language guide.

- **No top-of-funnel "I have Heddle running, now what?" pathway.**
  README.md and `docs/index.md` describe the SDK in terms of "build the
  package and run the echo example." A reader who already has a Heddle
  router/Workshop running and wants their first cross-language worker
  has to read CONCEPTS → GETTING_STARTED → WORKSHOP → NATS → DOTNET/SWIFT.
  Consider a "First worker against live Heddle" recipe that links the
  three commands they actually need: start NATS, `heddle router
  --nats-url`, run the .NET/Swift example pointed at NATS instead of
  the in-memory transport.

- **AGENTS.md points at toolkit anchors; user-facing docs don't.**
  AGENTS.md:22-27 names ECOSYSTEM/PHILOSOPHY/INVARIANTS/CONTRACT_MAP.
  None of `docs/*.md` references the toolkit anchors. A contributor
  who lands on `docs/CONTRIBUTING.md` is told to read upstream
  governance/invariants but not the cross-repo invariants C1–C7 that
  the toolkit owns (and that AGENTS.md:98-103 already cites as
  authoritative for this repo). Add one line in CONTRIBUTING.md and
  ARCHITECTURE.md: "Cross-repo invariants live in
  `heddle-agent-toolkit/anchors/INVARIANTS.md` (C1–C7 govern this
  repo)."

- **No quick reference for `Subjects` constants.** The .NET/Swift
  language guides describe `RunAsync` / `run(transport:)` but never
  show the `Subjects` helper API surface (`IncomingTasks`,
  `DeadLetters`, `IncomingGoals`, `ControlReload`, `WorkerTasks(...)`,
  `Results(...)`). A worker author who wants to publish a task
  manually will hunt through `Subjects.cs` directly. A small table
  in CONCEPTS.md or a "Subject helpers" subsection in DOTNET/SWIFT
  would close this gap.

- **No `swift-nats` minimal example.** `examples/swift/echo-worker`
  uses `InMemoryTransport` only. The Swift docs (SWIFT.md:101-109,
  NATS.md:80-86) show a `NatsTransport` snippet inline but there is
  no runnable Swift NATS example to copy. The .NET side is in the
  same situation — `examples/dotnet/EchoWorker` is in-memory only.
  Either add a NATS-mode flag to the existing examples or add
  `examples/{dotnet,swift}/EchoWorkerNats/`.

## Cross-repo coherence notes

- **Subject naming is internally consistent.** SDK uses
  `heddle.results.{parent_task_id or "default"}` everywhere
  (README.md:100, CONCEPTS.md:37, NATS.md:99, WORKSHOP.md:59,
  EXAMPLES.md:33, PORTING.md:75), and this matches upstream
  `heddle/docs/foreign-actors.md:68,145-146` and the vendored
  `task_result.schema.json:15`. There is a discrepancy between the
  SDK docs (use `parent_task_id`) and the toolkit's
  `CONTRACT_MAP.md` (uses `{goal_id}`) — but the SDK docs and
  upstream foreign-actors.md agree. **The toolkit anchor is the
  one out of step**, not the SDK docs. Flagging here for the parent
  agent; do not change the SDK docs to match the toolkit.

- **Queue-group naming is correct everywhere:** `processors-{worker_type}`
  is consistent across README.md, CONCEPTS.md, NATS.md, WORKSHOP.md,
  PORTING.md, and matches toolkit `INVARIANTS.md` C2 and
  `CONTRACT_MAP.md` queue-group table.

- **Build commands are correct.** All `dotnet build`, `dotnet test`,
  `swift build --package-path swift{,-nats}` paths verified against
  the filesystem. `python tools/sync_schemas.py --check` script
  exists. `docs/diagrams/make_dark_variants.py` exists. AGENTS.md
  verification commands and CONTRIBUTING.md PR checklist run.

- **No dead relative links found in docs/*.md.** All `(FOO.md)`
  references resolve to existing files in `docs/`.

- **No dead `../heddle/...` links.** AGENTS.md:39 references
  `../heddle/docs/foreign-actors.md` — exists. No other relative
  cross-repo links in user-facing docs (CONTRIBUTING uses absolute
  GitHub URLs).

- **Recent-refactor leftovers (toolkit deferral):** AGENTS.md was
  slimmed appropriately. The only restatement of toolkit-owned
  content in `docs/` is the wire-protocol summary in CONCEPTS.md and
  README.md, which is reasonable since CONCEPTS is the SDK reader's
  entry point and the toolkit's CONTRACT_MAP is agent-facing. No
  action needed there. The bigger gap is the opposite direction:
  user-facing docs don't *mention* the toolkit at all (covered in
  Discoverability Gaps).
