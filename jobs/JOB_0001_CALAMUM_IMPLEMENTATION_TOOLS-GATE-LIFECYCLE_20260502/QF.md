# CALAMUM_JOB_0001 · Tools Gate Lifecycle · 2026-05-02

## Metadata

- Task ID: `calamum-job-0001-tools_gate_lifecycle-20260502`
- Artifact role: `required human-facing frame-stack projection`
- Authority posture: derived from supplemental execution detail in `QS.json`; registered state remains authoritative in `operations/tasks.json`
- Status: `completed`
- Status authority: `operations/tasks.json`
- Last Transition (UTC): `2026-05-02T19:33:38.933033Z`
- Updated By: `ORACL-Prime`
- Auto-sync fields: `Status ; Last Transition (UTC) ; Updated By`
- Rewrite boundary: `Only sanctioned metadata fields may be rewritten during lifecycle transitions; all other document content is immutable under header auto-sync.`
- Project: `calamum`
- Scope: `project`
- Routing version: `job-routing-v1`
- Created (UTC): `2026-05-02T07:33:01.250255Z`
- Owner: `ORACL-Prime`
- Artifact kind: `human-facing-frame-stack-projection`
- Source of truth: `projects/calamum/jobs/JOB_0001_CALAMUM_IMPLEMENTATION_TOOLS-GATE-LIFECYCLE_20260502/QS.json` for supplemental execution detail; `operations/tasks.json` for state
- Current Focus Frame: `qf7`
- Mutation posture: `regenerated from QS.json under the authority spine; never treated as a peer mutation surface`
- Frame schema version: `job-frame-stack/v1`

## Lane summary

Calamum monitor scaffolding implementation for native evidence orchestration readiness gates

## Current execution state

- Last recorded QuestStack focus frame: `qf7`
- Lifecycle posture: `completed` in `operations/tasks.json`
- Active frame state: Frame qf7 completed; all declared frames are processed and the task close is committed.
- Active frame goal: Package the completed planning outputs into a clean execution-ready handoff that can drive implementation without placeholder drift, authority confusion, or premature claims that downstream Vulcan blockers are already resolved.

## Governance and authority spine

Current authority lives in:

- `docs/policies/operations/OPERATIONS_POLICY/PP_OPS_PROTOCOL_POL_JOB_PIPELINE_AUTHORITY_AND_EXECUTION_ARTIFACTS_20260312.md`
- `docs/operations/ssot/JOBS_AND_EXECUTION_SSOT.md`
- `operations/tasks.json`

## Containment rule and carry-in contract

### Carry-in tasks

- Verify that each preceding frame produced the required authority lock, compatibility map, evidence/monitor contracts, consumer mapping, and first-slice validation plan.
- Regenerate `JOB.md` canonically from the final `JOB.json` state and confirm the reader projection matches the machine-readable scaffold.
- Write the explicit implementation handoff packet: chosen slice, exact mutation files, validation matrix, deferments, and downstream unblock criteria.
- Record remaining risks and boundary conditions, including anything that still prevents Vulcan from resuming or prevents live capture from becoming in-scope.
- Prepare the lane for the next start/admission step without performing job close or claiming completed implementation.

### Containment rules

- This frame packages planning outputs and regenerates derived readers; it does not execute implementation or close the job.
- Be explicit about what remains blocked or deferred instead of smoothing it over in summary prose.
- Keep `JOB.md` generation on the canonical refresh-only path from `JOB.json`.

## Realignment reminders and drift-prevention discipline

### Realignment reminders

- Execution-ready is not the same thing as completed or close-ready.
- Derived projections must be regenerated from authoritative machine-readable state.
- Downstream unblock claims require native Calamum capability, not just a pretty plan.

### Drift-prevention rules

- Do not treat execution-ready planning as proof that downstream native capability already exists.
- Do not hand-edit derived reader artifacts to compensate for missing machine-readable detail.
- Do not collapse lifecycle close requirements into this handoff frame without explicit operator direction.

## Full predeclared frame stack

| Frame | Title | Status |
| --- | --- | --- |
| qf1 | Authority, corpus lock, and command surface freeze | completed |
| qf2 | Current substrate and compatibility map | completed |
| qf3 | Project evidence architecture and retention contract | completed |
| qf4 | Monitor shell, presets, and readiness/no go contract | completed |
| qf5 | Downstream Vulcan consumer mapping and adapter boundary | completed |
| qf6 | Minimum viable implementation slice and validation plan | completed |
| qf7 | Execution ready handoff and downstream unblock packet | completed |

## Per-frame status and next-action view

| Frame | Goal | Next action |
| --- | --- | --- |
| qf1 | Reconfirm the authoritative planning corpus and freeze the target operator-facing command grammar for standalone Calamum before any implementation slice is selected. | Advance to qf2 and map the live CLI/API/report/signing substrate against the frozen top-level grammar, compatibility aliases, and retained-evidence boundary. |
| qf2 | Map the live Calamum CLI, API, project, run, report, signing, catalog, and rendering seams into an explicit compatibility matrix for the accepted top-level expansion path. | Advance to qf3 and freeze the minimum viable `calamum project evidence` contract around the already-implemented project context, retained runs, aggregate reports, manifests, checksums, and signing helpers. |
| qf3 | Define the canonical project-scoped evidence route, retained artifact contract, and compatibility posture for runs, sessions, reports, verification, export, and aggregate review. | Freeze the minimum viable `calamum project evidence` surface, map it onto current retained artifacts, and document what stays canonical versus deferred. |
| qf4 | Freeze the canonical `calamum monitor` surface, preset vocabulary, readiness/no-go packet contract, and hidden adapter boundary needed for native monitoring without operator-facing backend drift. | Define the minimum viable monitor groups, preset ids, readiness packet fields, and `--json` noninteractive behavior while keeping backend tooling names internal. |
| qf5 | Translate the current Vulcan PIT/S3 monitor scripts and blocker posture into Calamum-native consumer requirements, preset candidates, and explicit unblock criteria without letting downstream consumer behavior redefine Calamum authority. | Map each current Vulcan script to a future native monitor/session route, record the blocker evidence it depends on, and freeze what Calamum must emit before Vulcan can be unblocked. |
| qf6 | Select the first bounded implementation slice, exact file-mutation order, and consolidated `calamum test` validation matrix needed to execute the accepted monitor/project-evidence expansion safely. | Choose the minimum viable first slice, freeze the file-level mutation order, and define the exact `calamum test`-orchestrated validation lanes that must accompany that slice. |
| qf7 | Package the completed planning outputs into a clean execution-ready handoff that can drive implementation without placeholder drift, authority confusion, or premature claims that downstream Vulcan blockers are already resolved. | Completed; no further frame action is currently registered. |

## Full per-frame narrative view

### Frame qf1 — Authority, corpus lock, and command surface freeze

- Status: `completed`
- Active focus frame: `false`
- Goal: Reconfirm the authoritative planning corpus and freeze the target operator-facing command grammar for standalone Calamum before any implementation slice is selected.
- Why this frame exists: The job needs a real opening frame that separates authority, planning, and runtime command-shape decisions from downstream implementation detail. This prevents the earlier single-frame overload and stops proposal text, package naming drift, or backend nouns from becoming accidental authority.

#### Execution plan

- Plan summary: Read the first-order authority spine (`operations/tasks.json`, policy SSOT, and the job pair)
- Planned actions:
  - ingest the proposal, the monitor/evidence scratchpad, the v1 plan, the v2 boundary note, `.calamum/project.json`, and `pyproject.toml`, then freeze the accepted top-level command grammar, project-scoped evidence routing, backend-name non-goals, and the `calamum` runtime versus `calamum-test` distribution boundary.

#### Results

- Outcome summary: Executed a corpus readback across the declared qf1 evidence routes and locked the active planning basis for this lane.
- Key results:
  - The accepted operator-facing grammar is `calamum test`, `calamum monitor`, and `calamum project`, with retained run/session/report retrieval routed through `calamum project evidence`.
  - Backend-facing tool names such as PyShark, TShark, dumpcap, USBPcap, Heimdall, or Windows PnP remain adapter/readiness metadata rather than primary operator nouns.
  - The v2 planning note remains exploratory except for silent Polymath integration, and the current `calamum-test` descriptor/package identity is treated as distribution metadata rather than as a replacement for the standalone `calamum` runtime/CLI identity frozen here.

#### Interpretation of results

- Interpretation summary: qf1 achieved its purpose: authority, corpus, and command-shape drift are now bounded before implementation-slice selection begins.
- Decision implications:
  - The lane can move into qf2 without reopening the top-level command-family debate, without elevating exploratory v2 ideas into active canon, and without letting backend tool names or package metadata redefine the user-facing Calamum identity.

#### Evidence routes

- `projects/calamum/jobs/JOB_0001_CALAMUM_IMPLEMENTATION_TOOLS-GATE-LIFECYCLE_20260502/CALAMUM_MONITOR_EVIDENCE_ARCHITECTURE_PROPOSAL_20260501.md`
- `projects/calamum/jobs/JOB_0001_CALAMUM_IMPLEMENTATION_TOOLS-GATE-LIFECYCLE_20260502/CALAMUM_MONITOR_EVIDENCE_ARCHITECTURE_SCRATCHPAD_20260501.md`
- `projects/calamum/planning/CALAMUM_TEST_CHILD_REPO_IMPLEMENTATION_PLAN_20260423.md`
- `projects/calamum/planning/CALAMUM_TEST_V2_TARGETS_20260423.md`
- `projects/calamum/.calamum/project.json`
- `projects/calamum/pyproject.toml`

#### Validation summary

- `pytest`: `deferred` — This frame freezes grammar and authority. Pytest execution remains deferred until the later implementation slice is selected. (basis: pre-start planning scaffold)
- `sandbox test`: `deferred` — Help/JSON snapshots are declared now and executed only after implementation exists. (basis: pre-start planning scaffold)
- `empirical test`: `executed` — Completed a manual corpus reconciliation across the declared qf1 authority and planning surfaces to lock the accepted command grammar, identity split, and non-goals before advancing the frame stack. (evidence: `projects/calamum/jobs/JOB_0001_CALAMUM_IMPLEMENTATION_TOOLS-GATE-LIFECYCLE_20260502/CALAMUM_JOB_PIPELINE_SSOT_AUDIT_SCRATCHPAD_20260502.md`) (basis: authoritative qf1 corpus readback)

### Frame qf2 — Current substrate and compatibility map

- Status: `completed`
- Active focus frame: `false`
- Goal: Map the live Calamum CLI, API, project, run, report, signing, catalog, and rendering seams into an explicit compatibility matrix for the accepted top-level expansion path.
- Why this frame exists: The proposal assumes a strong retained-evidence substrate already exists. This frame turns that assumption into a file-level compatibility map so later work reuses live substrate instead of re-implementing it or breaking existing `calamum test` behavior.

#### Execution plan

- Plan summary: Read the current Calamum CLI, API facade, project-resolution layer, retained-run engine, aggregate-report engine, signing helpers, catalog schema, layout helpers, renderers, and CLI tests
- Planned actions:
  - then distinguish what is already generic/reusable from what is still route-bound to the current `calamum test` namespace and therefore likely to change when `calamum project` and `calamum monitor` become first-class top-level families.

#### Results

- Outcome summary: Mapped the live substrate and compatibility surface.
- Key results:
  - Today only `calamum test` exists at the top level, and the nested families `project`, `runs`, and `reports` hang below it in `cli.py`.
  - The reusable substrate is already stronger than the current command tree suggests: `projects.py` owns project registration, active-state persistence, alias resolution, overlays, and path-root derivation
  - `runner.py` owns retained run execution, manifests, checksums
  - run index writes
  - `reports.py` owns aggregate generation, receipts, history, and optional signatures
  - `signing.py` owns canonical JSON signing/verification and checksum sidecars
  - `catalog.py`, `layout.py`, and `render.py` already provide schema, output-root, and human/JSON rendering contracts that can survive route migration.
  - `api.py` is a thin facade over these reusable modules.
  - The most likely mutation surface for the planned expansion is therefore CLI dispatch/help/output tests plus thin API/README/security adjustments, not a rewrite of the retained-evidence core.

#### Interpretation of results

- Interpretation summary: qf2 confirms the proposal’s premise: the retained-evidence substrate already exists and is largely route-agnostic.
- Decision implications:
  - Future `calamum project` and `calamum monitor` work should prefer re-routing and facade expansion over duplicating runner/report/signing/storage logic.
  - Compatibility obligations are real because `tests/test_cli.py` currently asserts grouped help, `calamum test project ...`, retained runs, and retained reports behavior, so canonical expansion must preserve or deliberately alias those surfaces while the top-level families are introduced.

#### Evidence routes

- `projects/calamum/src/calamum/cli.py`
- `projects/calamum/src/calamum/api.py`
- `projects/calamum/src/calamum/projects.py`
- `projects/calamum/src/calamum/runner.py`
- `projects/calamum/src/calamum/reports.py`
- `projects/calamum/src/calamum/signing.py`
- `projects/calamum/src/calamum/catalog.py`
- `projects/calamum/src/calamum/layout.py`
- `projects/calamum/src/calamum/render.py`
- `projects/calamum/catalog/test_definitions.json`
- `projects/calamum/tests/test_cli.py`

#### Validation summary

- `pytest`: `deferred` — Pytest candidates are anchored to the compatibility map but remain deferred until the mutation slice is chosen. (basis: pre-start planning scaffold)
- `sandbox test`: `deferred` — CLI help and path-layout probes are planned outputs for post-mutation validation. (basis: pre-start planning scaffold)
- `empirical test`: `executed` — Completed a live file-level seam review across the current CLI, API, project, run, report, signing, catalog, layout, render, and CLI-test surfaces to freeze the qf2 compatibility map. (evidence: `projects/calamum/jobs/JOB_0001_CALAMUM_IMPLEMENTATION_TOOLS-GATE-LIFECYCLE_20260502/CALAMUM_JOB_PIPELINE_SSOT_AUDIT_SCRATCHPAD_20260502.md`) (basis: live substrate/code readback)

### Frame qf3 — Project evidence architecture and retention contract

- Status: `completed`
- Active focus frame: `false`
- Goal: Define the canonical project-scoped evidence route, retained artifact contract, and compatibility posture for runs, sessions, reports, verification, export, and aggregate review.
- Why this frame exists: Project evidence is the backbone that lets Calamum grow beyond `calamum test` without losing retained evidence discipline. This frame prevents later implementation from collapsing into ad hoc report routing or evidence duplication.

#### Execution plan

- Goal: Define the canonical project-scoped evidence route, retained artifact contract, and compatibility posture for runs, sessions, reports, verification, export, and aggregate review.
- Current execution state: pending
- Next action: Freeze the minimum viable `calamum project evidence` surface, map it onto current retained artifacts, and document what stays canonical versus deferred.
- Carry-in tasks:
  - Define the minimum viable `calamum project` and `calamum project evidence` grammar needed for this lane, including `project set`, `project clear`, and the first retained-evidence verbs.
  - Map existing retained run and report artifacts onto future evidence references, manifests, checksums, receipts, and optional signatures.
  - Freeze which evidence operations are in the first slice versus explicitly deferred (`verify`, `bundle`, `export`, `index`, or richer session families where needed).
  - Define publishable/local-only boundaries, path-redaction expectations, and project-relative review/open flows for human-facing surfaces.
  - Document compatibility aliases from current `calamum test runs/reports/project` behavior into future canonical routes.
- Scenario focus:
  - `project set/clear ergonomics`
  - `project-scoped evidence review`
  - `retained artifact reuse`
  - `local-only versus publishable evidence boundaries`
- Realignment reminders:
  - Evidence is project-scoped; do not flatten it into a route that ignores project context.
  - Reuse manifests, checksums, receipts, and signing helpers already present in the substrate.
  - Prefer explicit deferments over quietly overcommitting a first implementation slice.
- Notes: Favor the lowest-risk first slice: evidence routes that reuse existing run/report/signing roots and preserve compatibility aliases from nested `test` routes.

#### Results

- Current execution state: pending
- Notes: Favor the lowest-risk first slice: evidence routes that reuse existing run/report/signing roots and preserve compatibility aliases from nested `test` routes.
- Registered exit criteria:
  - The minimum viable `project` and `project evidence` contract is explicit and bounded.
  - Evidence packet fields and storage/review routes are mapped to existing Calamum retention substrate.
  - Compatibility, local-only, and publishable-boundary rules are documented clearly enough for implementation handoff.

#### Interpretation of results

- No explicit interpretation is currently recorded in `QS.json`.
- Current frame status: `completed`
- Current execution state: pending
- Current next action: Freeze the minimum viable `calamum project evidence` surface, map it onto current retained artifacts, and document what stays canonical versus deferred.

#### Evidence routes

- `projects/calamum/README.md`
- `projects/calamum/SECURITY.md`
- `projects/calamum/src/calamum/projects.py`
- `projects/calamum/src/calamum/runner.py`
- `projects/calamum/src/calamum/reports.py`
- `projects/calamum/src/calamum/signing.py`
- `projects/calamum/src/calamum/layout.py`
- `projects/calamum/src/calamum/render.py`

#### Validation summary

- `pytest`: `deferred` — Evidence-route validation is declared here and executed only after the first mutation slice is admitted. (basis: pre-start planning scaffold)
- `sandbox test`: `deferred` — CLI and retained-output probes are planned for post-mutation validation. (basis: pre-start planning scaffold)
- `empirical test`: `deferred` — Security and publication-boundary review is a declared later validation lane. (basis: pre-start planning scaffold)

### Frame qf4 — Monitor shell, presets, and readiness/no go contract

- Status: `completed`
- Active focus frame: `false`
- Goal: Freeze the canonical `calamum monitor` surface, preset vocabulary, readiness/no-go packet contract, and hidden adapter boundary needed for native monitoring without operator-facing backend drift.
- Why this frame exists: Monitor scaffolding is the piece that blocks downstream Vulcan evidence work. This frame turns the proposal into an implementable monitor contract before any adapter or CLI mutation begins.

#### Execution plan

- Goal: Freeze the canonical `calamum monitor` surface, preset vocabulary, readiness/no-go packet contract, and hidden adapter boundary needed for native monitoring without operator-facing backend drift.
- Current execution state: pending
- Next action: Define the minimum viable monitor groups, preset ids, readiness packet fields, and `--json` noninteractive behavior while keeping backend tooling names internal.
- Carry-in tasks:
  - Freeze the top-level `monitor` grammar and minimum viable subgroups (`pnp`, `pcap`, `session`, and any capability/readiness readback needed for diagnostics).
  - Define the preset/pattern vocabulary, required preset fields, local overlay expectations, and the exact role of `--pattern` versus tracked presets.
  - Define the automated readiness/no-go packet shape, including project resolution, backend capability discovery, privilege status, decision/result fields, and retry guidance.
  - Map retained monitor-session evidence fields onto the same manifest/checksum/signature conventions used by current test/report substrate.
  - Record the explicit rule that backend tool names may appear in retained metadata and diagnostics but not as primary operator command families.
- Scenario focus:
  - `monitor shell grammar`
  - `preset/pattern model`
  - `readiness/no-go packets`
  - ``--json` noninteractive behavior`
  - `hidden backend-adapter boundary`
- Realignment reminders:
  - Automated gates belong inside native monitor commands; do not require separate operator preflight rituals for ordinary flows.
  - `--json` is the canonical noninteractive trigger and must emit no-prompt go/no-go packets.
  - Do not assume PyShark alone proves live capture readiness; system backends remain separate readiness evidence.
- Notes: The target is a Calamum-native monitor shell with evidence-rich fail-closed behavior, not a thin wrapper that exposes PyShark/TShark/USBPcap directly to operators.

#### Results

- Current execution state: pending
- Notes: The target is a Calamum-native monitor shell with evidence-rich fail-closed behavior, not a thin wrapper that exposes PyShark/TShark/USBPcap directly to operators.
- Registered exit criteria:
  - The minimum viable `monitor` contract is explicit and bounded.
  - Preset, readiness, and evidence-packet schema expectations are frozen for implementation handoff.
  - The adapter boundary is defined well enough to keep backend names out of primary operator grammar.

#### Interpretation of results

- No explicit interpretation is currently recorded in `QS.json`.
- Current frame status: `completed`
- Current execution state: pending
- Current next action: Define the minimum viable monitor groups, preset ids, readiness packet fields, and `--json` noninteractive behavior while keeping backend tooling names internal.

#### Evidence routes

- `projects/calamum/jobs/JOB_0001_CALAMUM_IMPLEMENTATION_TOOLS-GATE-LIFECYCLE_20260502/CALAMUM_MONITOR_EVIDENCE_ARCHITECTURE_PROPOSAL_20260501.md`
- `projects/calamum/jobs/JOB_0001_CALAMUM_IMPLEMENTATION_TOOLS-GATE-LIFECYCLE_20260502/CALAMUM_MONITOR_EVIDENCE_ARCHITECTURE_SCRATCHPAD_20260501.md`
- `projects/calamum/README.md`
- `projects/calamum/SECURITY.md`
- `projects/calamum/src/calamum/api.py`
- `projects/calamum/src/calamum/projects.py`
- `projects/calamum/src/calamum/signing.py`

#### Validation summary

- `pytest`: `deferred` — Monitor-contract tests are declared here and executed after implementation work begins. (basis: pre-start planning scaffold)
- `sandbox test`: `deferred` — Help and no-go JSON probes remain future validation lanes. (basis: pre-start planning scaffold)
- `empirical test`: `deferred` — Architecture and packet-quality review is declared for later execution. (basis: pre-start planning scaffold)

### Frame qf5 — Downstream Vulcan consumer mapping and adapter boundary

- Status: `completed`
- Active focus frame: `false`
- Goal: Translate the current Vulcan PIT/S3 monitor scripts and blocker posture into Calamum-native consumer requirements, preset candidates, and explicit unblock criteria without letting downstream consumer behavior redefine Calamum authority.
- Why this frame exists: Vulcan is the clearest downstream consumer, but it is blocked today. This frame captures the exact consumer needs Calamum must satisfy while preventing the job from drifting into a Vulcan-owned identity or script-first command surface.

#### Execution plan

- Goal: Translate the current Vulcan PIT/S3 monitor scripts and blocker posture into Calamum-native consumer requirements, preset candidates, and explicit unblock criteria without letting downstream consumer behavior redefine Calamum authority.
- Current execution state: pending
- Next action: Map each current Vulcan script to a future native monitor/session route, record the blocker evidence it depends on, and freeze what Calamum must emit before Vulcan can be unblocked.
- Carry-in tasks:
  - Map `run_gui_pit_continuous_monitor.py`, `run_pit_transport_diagnostic.py`, and `run_gui_pit_evidence_session.py` into future Calamum-native `monitor` groups, presets, and evidence outputs.
  - Record which retained evidence fields, readiness packets, and session outputs Vulcan actually needs for PIT/S3 remediation and approval-grade readback.
  - Freeze the explicit downstream unblock contract: what native Calamum monitor/project-evidence capability must exist before Vulcan should resume.
  - Separate consumer-only requirements from reusable Calamum core substrate so Vulcan-specific behavior does not pollute generic monitor design.
  - Document any still-open risks (wrong-interface binding, transport nonconvergence, live capture sensitivity) as consumer constraints rather than Calamum identity.
- Scenario focus:
  - `Vulcan PIT/S3 consumer needs`
  - `preset/adaptor mapping`
  - `downstream unblock criteria`
  - `consumer-only versus core-substrate boundaries`
- Realignment reminders:
  - Vulcan is not the authority surface for this job; it is a downstream consumer requirement source.
  - Keep live PIT/S3 capture and hardware-facing action out of this planning frame.
  - Use downstream behavior references to define acceptance needs, not command-family ownership.
- Notes: Treat Vulcan as a downstream consumer scenario. Do not reopen blocked Vulcan execution work inside this standalone Calamum planning lane.

#### Results

- Current execution state: pending
- Notes: Treat Vulcan as a downstream consumer scenario. Do not reopen blocked Vulcan execution work inside this standalone Calamum planning lane.
- Registered exit criteria:
  - Each relevant Vulcan script has a mapped future Calamum-native route or an explicit deferment.
  - The downstream unblock contract is explicit enough to prevent premature Vulcan reruns.
  - Consumer-specific requirements are separated cleanly from standalone Calamum command authority.

#### Interpretation of results

- No explicit interpretation is currently recorded in `QS.json`.
- Current frame status: `completed`
- Current execution state: pending
- Current next action: Map each current Vulcan script to a future native monitor/session route, record the blocker evidence it depends on, and freeze what Calamum must emit before Vulcan can be unblocked.

#### Evidence routes

- `projects/calamum-vulcan/tools/run_gui_pit_continuous_monitor.py`
- `projects/calamum-vulcan/tools/run_pit_transport_diagnostic.py`
- `projects/calamum-vulcan/tools/run_gui_pit_evidence_session.py`
- `operations/tasks.json`
- `projects/calamum/jobs/JOB_0001_CALAMUM_IMPLEMENTATION_TOOLS-GATE-LIFECYCLE_20260502/CALAMUM_MONITOR_EVIDENCE_ARCHITECTURE_PROPOSAL_20260501.md`

#### Validation summary

- `pytest`: `deferred` — Downstream parity tests are declared but remain deferred until native routes exist. (basis: pre-start planning scaffold)
- `sandbox test`: `deferred` — Session/report probes remain future validation work after implementation. (basis: pre-start planning scaffold)
- `empirical test`: `deferred` — Conceptual replay is planned once the native contract is formalized in-frame. (basis: pre-start planning scaffold)

### Frame qf6 — Minimum viable implementation slice and validation plan

- Status: `completed`
- Active focus frame: `false`
- Goal: Select the first bounded implementation slice, exact file-mutation order, and consolidated `calamum test` validation matrix needed to execute the accepted monitor/project-evidence expansion safely.
- Why this frame exists: Earlier frames establish contracts; this frame converts them into an execution-ready mutation and validation packet so the eventual implementation work has explicit file scope, compatibility obligations, and evidence requirements.

#### Execution plan

- Goal: Select the first bounded implementation slice, exact file-mutation order, and consolidated `calamum test` validation matrix needed to execute the accepted monitor/project-evidence expansion safely.
- Current execution state: pending
- Next action: Choose the minimum viable first slice, freeze the file-level mutation order, and define the exact `calamum test`-orchestrated validation lanes that must accompany that slice.
- Carry-in tasks:
  - Compare candidate first slices and select the lowest-risk route that materially advances native `project`/`monitor` scaffolding without breaking current `calamum test` behavior.
  - Freeze the exact file-mutation order for the chosen slice, including code, tests, and any required README/SECURITY adjustments.
  - Define the consolidated `calamum test` validation plan across pytest, sandbox, and empirical lanes, including alias parity, JSON/no-go packets, and retained-evidence review.
  - Record any explicit deferments or override-sensitive validations so later implementation work does not hide them.
  - Document what downstream unblock evidence the first slice can satisfy immediately versus what remains for later follow-on work.
- Scenario focus:
  - `first mutation slice selection`
  - `file-level mutation order`
  - ``calamum test` validation matrix`
  - `explicit deferments and follow-ons`
- Realignment reminders:
  - All code-change validation in this repo routes through `calamum test`; narrower pytest is supplemental evidence only.
  - Choose the smallest slice that proves the architecture without reopening command-shape debates.
  - Write down deferments explicitly rather than silently carrying them into implementation.
- Notes: The likely first slice is top-level `project` plus the first `project evidence` routes, `project set`/`project clear`, and a monitor command shell/readiness skeleton, but the frame must prove that choice against the compatibility matrix before locking it.

#### Results

- Current execution state: pending
- Notes: The likely first slice is top-level `project` plus the first `project evidence` routes, `project set`/`project clear`, and a monitor command shell/readiness skeleton, but the frame must prove that choice against the compatibility matrix before locking it.
- Registered exit criteria:
  - A first implementation slice is selected with explicit rationale and non-goals.
  - The exact mutation file set and validation matrix are frozen.
  - Deferred work and downstream-unblock boundaries are explicit enough to guide the next execution lane safely.

#### Interpretation of results

- No explicit interpretation is currently recorded in `QS.json`.
- Current frame status: `completed`
- Current execution state: pending
- Current next action: Choose the minimum viable first slice, freeze the file-level mutation order, and define the exact `calamum test`-orchestrated validation lanes that must accompany that slice.

#### Evidence routes

- `projects/calamum/src/calamum/cli.py`
- `projects/calamum/src/calamum/api.py`
- `projects/calamum/src/calamum/projects.py`
- `projects/calamum/src/calamum/runner.py`
- `projects/calamum/src/calamum/reports.py`
- `projects/calamum/tests/test_cli.py`
- `projects/calamum/README.md`
- `projects/calamum/SECURITY.md`

#### Validation summary

- `pytest`: `deferred` — This frame freezes the validation matrix; execution remains deferred until implementation begins. (basis: pre-start planning scaffold)
- `sandbox test`: `deferred` — Sandbox probes are selected here and executed after the chosen slice lands. (basis: pre-start planning scaffold)
- `empirical test`: `deferred` — Empirical review remains a declared future validation requirement. (basis: pre-start planning scaffold)

### Frame qf7 — Execution ready handoff and downstream unblock packet

- Status: `completed`
- Active focus frame: `true`
- Goal: Package the completed planning outputs into a clean execution-ready handoff that can drive implementation without placeholder drift, authority confusion, or premature claims that downstream Vulcan blockers are already resolved.
- Why this frame exists: A planning job of this size needs an explicit finish line. This frame turns the prior contract and slice work into a handoff packet that is safe for `codesentinel job start` execution, safe for derived-doc regeneration, and honest about what remains blocked or deferred.

#### Execution plan

- Goal: Package the completed planning outputs into a clean execution-ready handoff that can drive implementation without placeholder drift, authority confusion, or premature claims that downstream Vulcan blockers are already resolved.
- Current execution state: Frame qf7 completed; all declared frames are processed and the task close is committed.
- Next action: Completed; no further frame action is currently registered.
- Carry-in tasks:
  - Verify that each preceding frame produced the required authority lock, compatibility map, evidence/monitor contracts, consumer mapping, and first-slice validation plan.
  - Regenerate `JOB.md` canonically from the final `JOB.json` state and confirm the reader projection matches the machine-readable scaffold.
  - Write the explicit implementation handoff packet: chosen slice, exact mutation files, validation matrix, deferments, and downstream unblock criteria.
  - Record remaining risks and boundary conditions, including anything that still prevents Vulcan from resuming or prevents live capture from becoming in-scope.
  - Prepare the lane for the next start/admission step without performing job close or claiming completed implementation.
- Scenario focus:
  - `execution-ready handoff`
  - `derived-doc regeneration`
  - `explicit blocker/deferment statement`
  - `downstream unblock packet`
- Realignment reminders:
  - Execution-ready is not the same thing as completed or close-ready.
  - Derived projections must be regenerated from authoritative machine-readable state.
  - Downstream unblock claims require native Calamum capability, not just a pretty plan.
- Notes: This frame is about execution readiness and handoff quality, not lifecycle close. Do not conflate a complete planning packet with operator-approved job closure.

#### Results

- Current execution state: Frame qf7 completed; all declared frames are processed and the task close is committed.
- Notes: This frame is about execution readiness and handoff quality, not lifecycle close. Do not conflate a complete planning packet with operator-approved job closure.
- Registered exit criteria:
  - The job has a complete, bounded, multi-frame execution scaffold with no placeholder drift.
  - The implementation handoff packet is explicit enough to guide mutation without reopening core design questions.
  - Regenerated reader projections match the authoritative `JOB.json`.
  - Remaining blockers, deferments, and downstream-unblock boundaries are stated plainly.

#### Interpretation of results

- No explicit interpretation is currently recorded in `QS.json`.
- Current frame status: `completed`
- Current execution state: Frame qf7 completed; all declared frames are processed and the task close is committed.
- Current next action: Completed; no further frame action is currently registered.

#### Evidence routes

- `projects/calamum/jobs/JOB_0001_CALAMUM_IMPLEMENTATION_TOOLS-GATE-LIFECYCLE_20260502/JOB.json`
- `projects/calamum/jobs/JOB_0001_CALAMUM_IMPLEMENTATION_TOOLS-GATE-LIFECYCLE_20260502/JOB.md`
- `operations/tasks.json`
- `projects/calamum/jobs/JOB_0001_CALAMUM_IMPLEMENTATION_TOOLS-GATE-LIFECYCLE_20260502/CALAMUM_MONITOR_EVIDENCE_ARCHITECTURE_PROPOSAL_20260501.md`

#### Validation summary

- `pytest`: `deferred` — This frame confirms the validation matrix rather than executing it. (basis: pre-start planning scaffold)
- `sandbox test`: `deferred` — Reader projection regeneration and coherence checks are the main sandbox-facing outputs for this frame. (basis: pre-start planning scaffold)
- `empirical test`: `deferred` — Manual handoff quality review is planned when this frame becomes active. (basis: pre-start planning scaffold)

## Evidence and derived-report routing

- Supplemental execution-detail artifact: `projects/calamum/jobs/JOB_0001_CALAMUM_IMPLEMENTATION_TOOLS-GATE-LIFECYCLE_20260502/QS.json`
- Required derived reader surface: `projects/calamum/jobs/JOB_0001_CALAMUM_IMPLEMENTATION_TOOLS-GATE-LIFECYCLE_20260502/QF.md`
- Active-frame evidence routes:
  - `projects/calamum/jobs/JOB_0001_CALAMUM_IMPLEMENTATION_TOOLS-GATE-LIFECYCLE_20260502/JOB.json`
  - `projects/calamum/jobs/JOB_0001_CALAMUM_IMPLEMENTATION_TOOLS-GATE-LIFECYCLE_20260502/JOB.md`
  - `operations/tasks.json`
  - `projects/calamum/jobs/JOB_0001_CALAMUM_IMPLEMENTATION_TOOLS-GATE-LIFECYCLE_20260502/CALAMUM_MONITOR_EVIDENCE_ARCHITECTURE_PROPOSAL_20260501.md`
- Same-transition routing rule: mutate `QS.json` -> regenerate `QF.md` -> refresh dependent derived packets and reports.
