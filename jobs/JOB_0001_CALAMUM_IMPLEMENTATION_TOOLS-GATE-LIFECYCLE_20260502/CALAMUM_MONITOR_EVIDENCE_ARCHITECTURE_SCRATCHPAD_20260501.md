TL;DR: This scratchpad records the planning-only investigation for a native Calamum monitoring and evidence architecture. The recommended shape is `calamum monitor` for domain-oriented monitoring/capture, `calamum evidence` for retained runs, reports, bundles, retrieval, and verification, and continued `calamum test` ownership of test definition execution. PyShark and any TShark/USBPcap tooling should be hidden behind Calamum monitor adapters and never exposed as direct operator command families.

# Calamum monitor/evidence architecture scratchpad

## Status note

- Operator: `joediggidyyy`
- Planner: `ORACL-Prime`
- Date: `2026-05-01`
- Scope: planning and strategy only
- Implementation posture: no code changes authorized in this pass
- Authority posture: supporting planning artifact only; this file is not a first-order execution authority

Current first-order execution authority remains outside this scratchpad:

- `docs/policies/operations/OPERATIONS_POLICY/PP_OPS_PROTOCOL_POL_JOB_PIPELINE_AUTHORITY_AND_EXECUTION_ARTIFACTS_20260312.md`
- `docs/operations/ssot/JOBS_AND_EXECUTION_SSOT.md`
- `operations/tasks.json`

## Operator request captured

The operator requested a native Calamum design that:

- introduces a new top-level `calamum monitor` command family;
- routes PyShark and related monitoring/capture tooling through Calamum-native APIs/CLI only;
- avoids direct operator-facing third-party command names such as `calamum monitor pyshark`;
- keeps command families domain-oriented, such as `calamum monitor pcap ...` or `calamum monitor pnp ...`;
- integrates `calamum monitor` with `calamum test` through a shared document/orchestrator/evidence engine;
- separates report generation and evidence retrieval out of `calamum test` into a third top-level family;
- migrates Vulcan monitoring scripts into the Calamum monitor orchestrator;
- preserves Polymath-grade security, signed calls where appropriate, and retained evidence discipline;
- reduces operator load through predefined patterns/configs while keeping explicit flags available;
- defines policy, governance, support documents, artifacts, and edit targets required to compel canonical usage later;
- produces planning artifacts only in this pass.

## Corpus inspected in this planning pass

| Surface | Role in this investigation | Key finding |
| --- | --- | --- |
| `.github/instructions/execution-authority.instructions.md` | Governance constraint | Planning artifacts must not claim first-order lifecycle authority. Current authority references route through policy/SSOT/tasks. |
| `/memories/repo/calamum_dependency_distribution_vs_import_name_2026_04_23.md` | Naming constraint | Distribution is `calamum-test`; runtime import and CLI are `calamum`. |
| `/memories/repo/calamum_standalone_release_repo_local_artifact_ignore_2026_04_24.md` | Artifact hygiene | `.calamum/project.json` is publishable; generated `.calamum`, runs, reports, logs, and `.env` are local-only unless explicitly promoted. |
| `/memories/repo/codesentinel_code_changes_require_calamum_test_2026_04_30.md` | Validation constraint | Future code changes require rigorous `calamum test` validation; ad hoc pytest alone is not enough. |
| `projects/calamum/src/calamum/cli.py` | Existing command surface | Only top-level command currently supported is `calamum test`; `runs` and `reports` are nested under `test`. |
| `projects/calamum/src/calamum/runner.py` | Existing retained-run orchestrator | Executes definitions, captures stdout/stderr, writes `report.json`, `report.md`, `checksums.json`, `manifest.json`, and `run_index.jsonl`. |
| `projects/calamum/src/calamum/reports.py` | Existing aggregate report engine | Generates job/project/domain reports, manifests, receipts, checksums, and optional signatures. |
| `projects/calamum/src/calamum/signing.py` | Security/signature precedent | Supports canonical JSON signing and verification with Ed25519, HMAC-SHA256, or SHA256 fallback. |
| `projects/calamum/src/calamum/projects.py` | Project/context model | Provides `.calamum/project.json`, local overlays, active project state, path aliases, trusted requesters, and containment checks. |
| `projects/calamum/catalog/test_definitions.json` | Existing catalog model | Test definitions are cataloged with lanes, profiles, tags, policy flags, and evidence requirements. |
| `projects/calamum/README.md` | Product contract | Retained evidence and aggregate reports are explicit Calamum product promises. |
| `projects/calamum/SECURITY.md` | Security posture | Privileged generation must verify signatures and fail closed. |
| `projects/calamum/planning/CALAMUM_TEST_CHILD_REPO_IMPLEMENTATION_PLAN_20260423.md` | Calamum v1 plan | Project descriptors, API facade, signed privileged flows, report generation, and retained evidence are approved v1 primitives. |
| `projects/calamum/planning/CALAMUM_TEST_V2_TARGETS_20260423.md` | Boundary note | Silent Polymath application integration is the only explicitly approved v2 direction; broader ideas need explicit elevation. |
| `projects/calamum-vulcan/tools/run_gui_pit_continuous_monitor.py` | Current Vulcan passive monitor | Captures Windows USB/PnP timeline and token ownership evidence. |
| `projects/calamum-vulcan/tools/run_pit_transport_diagnostic.py` | Current Vulcan diagnostic | Runs Heimdall runtime probe, parser/fallback matrix, live PIT commands, Windows snapshots, and known-issue classification. |
| `projects/calamum-vulcan/tools/run_gui_pit_evidence_session.py` | Current Vulcan session orchestrator | Combines monitor timeline, operator GUI action window, post-GUI diagnostic, rollup, artifacts, and frame-stack next action. |
| `projects/calamum-vulcan/jobs/JOB_0001_CALAMUM-VULCAN_JOB_DOCS-REMEDIATION-PLANNING_20260501/QF.md` | Active frame projection | Frame stack is completed; current blocker is wrong-interface binding/non-converged PIT transport. |

## Current Calamum capabilities relevant to the design

Calamum already has enough primitives to become the host for native monitoring with limited conceptual expansion:

- project-aware context resolution via `.calamum/project.json` and local overlays;
- explicit run roots and report roots;
- tokenized command/path resolution;
- path containment checks for executed steps;
- retained stdout/stderr capture;
- per-run manifests and checksums;
- append-only run index;
- job/project/domain aggregate report generation;
- privileged request verification for aggregate generation;
- signed receipts and optional signed generated artifacts;
- stable Python facade under `calamum.api`.

The missing layer is not evidence retention. The missing layer is a first-class monitoring/capture domain model that can produce the same retained-evidence packets without hiding inside `calamum test` or Vulcan-local scripts.

## Current Vulcan monitor behavior to preserve

The Vulcan scripts currently preserve several high-value behaviors that should be migrated rather than lost:

1. `run_gui_pit_continuous_monitor.py`
   - passive Windows USB/PnP sampling;
   - focus-token owner mapping for Samsung `04E8:*` and observed non-Samsung tokens such as `04F2:*`;
   - timeline JSON and Markdown artifacts;
   - explicit warning that host visibility does not prove transport success.
2. `run_pit_transport_diagnostic.py`
   - deterministic PIT parser/fallback matrix;
   - Heimdall runtime probe;
   - optional live `print-pit` and `download-pit` through the Vulcan integrated runtime boundary;
   - pre/post Windows USB/PnP correlation;
   - known-issue classification, including `wrong_interface_binding`, `driver_rebind_in_flight`, and related families.
3. `run_gui_pit_evidence_session.py`
   - one mostly autonomous GUI/PIT evidence session;
   - monitor starts before the operator GUI action;
   - post-GUI live diagnostic runs automatically unless skipped with a reason;
   - minimum sample/duration controls;
   - combined conclusion and frame-stack next-action rollup.

## Active Vulcan evidence context

The current live blocker remains:

- blocker family: `wrong_interface_binding`
- active transport token: `04F2:B7EB:02`
- expected Samsung family: `04E8:*`
- current combined classification: `host_stable_transport_nonconverged`
- practical meaning: Windows can see Samsung/download-mode evidence, but PIT transport still binds to the wrong/non-Samsung lane.

This supports the need for S3-class discriminator capture, but future S3 capture should be invoked through `calamum monitor`, not by direct PyShark/TShark/USBPcap operator commands.

## Design decision log

### Decision 1 - recommend `calamum evidence` as the third top-level family

Recommendation: use `calamum evidence`, not `calamum report` or `calamum files`, as the canonical third family.

Rationale:

- report generation is only one function inside the broader retained-evidence lifecycle;
- users also need run/session lookup, artifact retrieval, bundle creation, signature/checksum verification, import/export, and index inspection;
- `evidence` is broad enough to hold `report`, `runs`, `sessions`, `bundle`, `verify`, and `export` without creating more top-level families later;
- `calamum report` can remain a future alias or a subcommand, but should not be the primary namespace if retrieval and file evidence are also in scope.

### Decision 2 - keep `calamum test` focused on execution definitions

`calamum test` should continue to own test-definition catalog execution and validation lane orchestration.

Candidate future responsibility split:

- `calamum test`: definitions, lanes, validation execution, test-run initiation.
- `calamum monitor`: capture/observe/instrument external or host runtime evidence.
- `calamum evidence`: retrieve, index, verify, aggregate, bundle, export, and render retained outputs.

The current `calamum test runs` and `calamum test reports` commands should become compatibility aliases after `calamum evidence` exists, not disappear abruptly.

### Decision 3 - hide external tools behind domain-oriented monitor types

Operator-facing examples should look like:

- `calamum monitor pnp snapshot ...`
- `calamum monitor pnp timeline ...`
- `calamum monitor pcap interfaces ...`
- `calamum monitor pcap capture ...`
- `calamum monitor session run --pattern vulcan-gui-pit ...`

They should not look like:

- `calamum monitor pyshark ...`
- `calamum monitor tshark ...`
- `calamum monitor usbpcapcmd ...`

Implementation may use PyShark/TShark/USBPcap internally, but the operator contract should remain Calamum-native.

### Decision 4 - use patterns for low-operator-load runs

Explicit flags must exist for automation and review, but ordinary operator flows should use predefined patterns:

- `vulcan-pnp-timeline`
- `vulcan-gui-pit-session`
- `vulcan-s3-usbpcap`
- `vulcan-pit-transport-diagnostic`

A single pattern should expand into capture type, sample interval, duration, output roots, required preflight checks, evidence requirements, and post-run report generation.

## Required conceptual modules for future implementation

| Future module | Purpose |
| --- | --- |
| `calamum.evidence` | Shared retained evidence store, run/session lookup, bundle/verify/export APIs. |
| `calamum.orchestrator` | Generic execution/session orchestration extracted from `runner.py` so tests and monitors share lifecycle logic. |
| `calamum.monitor` | Public monitor API facade and command dispatch entrypoints. |
| `calamum.monitor.patterns` | Pattern registry, schema validation, local overlay merge, and pattern expansion. |
| `calamum.monitor.adapters.pnp_windows` | Windows USB/PnP snapshot and timeline adapter. |
| `calamum.monitor.adapters.pcap` | Domain pcap orchestration facade hiding PyShark/TShark/USBPcap details. |
| `calamum.monitor.adapters.vulcan_pit` | Vulcan-specific session and PIT transport diagnostic adapter. |
| `calamum.security` or expanded `calamum.signing` | Shared signed request/receipt support for privileged monitor operations. |

## Immediate open design questions

1. Should `calamum evidence runs` preserve the word `runs`, or should monitor outputs introduce `sessions` as a sibling concept?
   - Recommendation: yes; use both. Test execution creates runs, monitor orchestration creates sessions, and both are evidence bundles.
2. Should `calamum test reports` remain indefinitely?
   - Recommendation: retain as a compatibility alias for one release family, then document `calamum evidence report ...` as canonical.
3. Should monitor patterns live in the existing `catalog/` root?
   - Recommendation: yes for tracked shared patterns, with local pattern overlays under the user config root.
4. Should PyShark become a required dependency of `calamum-test`?
   - Recommendation: no. Use an optional monitor extra or lazy adapter import; TShark/USBPcap remain system backends validated by preflight.
5. Does S3 USB capture require elevated privileges?
   - Recommendation: treat as privileged/high-risk until proven otherwise; require preflight, explicit operator confirmation or signed request, and retained backend capability evidence.

## Candidate next implementation sequence

1. Extract current run/report retrieval from `calamum test` into `calamum evidence` while keeping aliases.
2. Define evidence-bundle schema that can represent both test runs and monitor sessions.
3. Add monitor pattern registry and validation commands.
4. Add passive `pnp snapshot` and `pnp timeline` monitor commands first, because they map directly to current Vulcan scripts and avoid packet-capture backend complexity.
5. Add pcap preflight and interface listing next.
6. Add pcap capture only after backend checks and privilege/signature controls are implemented.
7. Migrate Vulcan monitor scripts into Calamum monitor adapters and leave thin project-local wrappers only if needed for transition.
8. Update Calamum README, SECURITY, planning, and schema docs.
9. Update Vulcan docs to require native Calamum monitor/evidence paths for future S3 evidence.
10. Update CodeSentinel authority surfaces only if/when the operator explicitly elevates these paths into lifecycle close/validation requirements.

## Non-goals for this planning pass

- No code implementation.
- No direct PyShark, TShark, Wireshark, USBPcap, or driver invocation.
- No live device capture.
- No job close.
- No mutation of first-order policy/SSOT authority documents.
- No claim that system Wireshark/TShark/USBPcap is installed merely because a Python package named `wireshark` was installed.

## Temporary discussion state - command shape refinement

> Temporary holding section. This captures the current discussion state for later integration into the official planning surface after the command hierarchy is approved. It is intentionally not final policy and should not be treated as the canonical implementation spec until reviewed.

### Current preferred top-level shape

The current preferred shape is Option B:

- `calamum test`
- `calamum monitor`
- `calamum project`

The important correction is that `project` should not remain nested under `test`. `test` and `monitor` are execution families. `project` owns durable context, configuration, definitions/patterns, trust, and retained evidence.

### Project command shape under discussion

Preferred direct project commands:

- `calamum project register`
- `calamum project set <project>` or possible rename `calamum project use <project>`
- `calamum project current`
- `calamum project validate`
- `calamum project list`
- `calamum project show <project>`

Preferred project resource families:

- `calamum project config ...`
- `calamum project definitions ...`
- `calamum project patterns ...`
- `calamum project trust ...`
- `calamum project evidence ...`

Operator preference note: avoid user-facing `catalog` language for this context. Use more concrete resource names such as `definitions` for test definitions and `patterns` for monitor patterns. Internally, Calamum can still store these in catalog-like JSON files, but the operator-facing command language should avoid `catalog` unless later explicitly approved.

### What `project set` means

`calamum project set <project>` is currently understood as setting a persistent active project pointer, not starting a live execution session.

In the existing Calamum implementation, the analogous command writes active-project state to the user Calamum config root:

- Windows default: `%APPDATA%/Calamum/state.json`
- XDG default: `${XDG_CONFIG_HOME}/calamum/state.json`
- fallback: `~/.config/calamum/state.json`
- override: `CALAMUM_CONFIG_ROOT`

The state record is a project pointer, not a secret token. Its core fields are expected to be:

- `schema_version`
- `active_project`
- `last_project`
- `recent_projects`

This active project is used only when a command needs project context and no higher-precedence context was supplied or discovered. Current/expected precedence remains:

1. explicit `--project <project>`
2. nearest ancestor `.calamum/project.json`
3. `CALAMUM_PROJECT`
4. active project from user state

Because this is a persistent default pointer, there is no session to end. To change it, run `calamum project set <other-project>`. A future `calamum project clear` or `calamum project unset` command may be useful if operators want to remove the active default entirely.

Open naming question: `set` is technically accurate but may be too generic. Alternatives:

| Candidate | Meaning | Notes |
| --- | --- | --- |
| `project set <project>` | Persist active project pointer | Matches current implementation vocabulary. |
| `project use <project>` | Make this the default project for later commands | More operator-friendly and common in multi-context CLIs. |
| `project activate <project>` | Activate a project context | Clear, but may imply a live session that needs deactivation. |

Current recommendation for discussion: prefer `calamum project use <project>` as the human-facing verb, with `set` retained as an alias if needed for compatibility.

### What `project current` does

`calamum project current` should read and explain the resolved project context for the current command environment.

It should not merely print an opaque session id. It should show the resolved project and why it was selected, including:

- project id;
- aliases;
- project root;
- descriptor path;
- active-state file path when relevant;
- resolution source, such as explicit flag, nearest descriptor, `CALAMUM_PROJECT`, or active state;
- catalog/definition root;
- runs/evidence root;
- reports root;
- relevant local overlay path;
- trusted requester summary;
- next useful validation command.

`project current` is helpful because it lets the operator verify what project Calamum will use before running `test`, `monitor`, or `project evidence` commands.

### Why active project state is useful

Active project state reduces repeated flags and keeps operator workflows concise when working across repositories or from outside the project root.

It is especially useful for:

- running Calamum from a neutral working directory;
- switching between CodeSentinel, Calamum, Vulcan, observer, or CIDS projects;
- keeping evidence/report roots stable without restating `--project` on every command;
- letting `monitor` and `test` share the same project resolution rules;
- supporting scripts that rely on the active project but still allow explicit `--project` override.

It is less important when the operator is already inside a project tree with a valid nearest `.calamum/project.json`, because nearest-descriptor resolution should usually be enough.

### Evidence shape already approved in discussion

Evidence is already considered project-scoped. The current preferred command shape is:

- `calamum project evidence runs list|show`
- `calamum project evidence sessions list|show`
- `calamum project evidence reports list|show|generate`
- `calamum project evidence bundle create`
- `calamum project evidence verify`
- `calamum project evidence export`

This keeps retained outputs attached to the project context that defines their roots, trust rules, aliases, and local overlays.

### Definitions and patterns instead of catalog

The current discussion rejects `catalog` as the primary user-facing term.

Preferred terms:

- `definitions` for reusable test definitions consumed by `calamum test`;
- `patterns` for reusable monitor patterns consumed by `calamum monitor`.

Candidate commands:

- `calamum project definitions list|show|validate|scaffold|add`
- `calamum project patterns list|show|validate|scaffold|add|disable|explain-schema`

Plain-language relationship:

- a definition or pattern is a reusable recipe;
- a run or session is an execution of a recipe;
- evidence is the retained output from that execution;
- reports are derived summaries from retained evidence.

### Trust shape requiring more detail

`calamum project trust ...` should own project-specific trust configuration.

Trust answers two questions:

1. Who may ask Calamum to perform privileged or official actions for this project?
2. How does Calamum prove what it did afterward?

Candidate commands:

- `calamum project trust list`
- `calamum project trust show`
- `calamum project trust validate`
- `calamum project trust add-requester <requester_id>`
- `calamum project trust remove-requester <requester_id>`
- `calamum project trust keys list|add|remove|validate`
- `calamum project trust request verify --request-file <path> --signature-file <path>`

Trust should be tiered:

| Tier | Example | Required control |
| --- | --- | --- |
| Local passive observation | `monitor pnp snapshot` | Project containment and retained evidence. |
| Privileged local capture | `monitor pcap capture --source usb` | Preflight plus operator confirmation or local policy approval. |
| Delegated official evidence | CodeSentinel or Vulcan requests official S3 capture | Signed request, trusted requester allowlist, expiry/nonce where supported, signed receipt. |
| Publishable/exported evidence | Evidence bundle leaves local project context | Signed manifest/report plus checksum verification. |

Superseding note from follow-up discussion: user-facing `project trust` commands are not needed in this lane. Trust/requester/user/role management belongs to a later user-management system and should be treated as v3 territory. Current monitor scaffolding should expose narrow internal hooks for future user-management integration, but should not ship a half-trust CLI.

### `project validate` versus `monitor preflight`

These functions still answer different questions internally, but they should not remain required user-orchestrated steps.

`calamum project validate` answers:

> Is this project definition/configuration coherent enough for Calamum to use?

It should validate durable/static project state:

- `.calamum/project.json` exists and parses;
- required markers and paths exist;
- aliases resolve deterministically;
- definitions and patterns parse and use approved vocabulary;
- runs/evidence/report roots are valid and contained;
- local overlay is readable where applicable;
- trust config is well-formed;
- shared config does not contain obvious secrets;
- project roots and path aliases do not unexpectedly escape allowed boundaries.

It usually should not require the live device, Wireshark, TShark, USBPcap, or capture privileges.

`calamum monitor preflight` answers:

> Can this exact monitor/capture operation run safely right now on this host?

It should validate volatile/runtime operation readiness:

- selected pattern expands correctly;
- OS supports the requested monitor type;
- optional adapter dependencies are importable if required;
- TShark/dumpcap/USBPcap paths and versions are available if required;
- capture interfaces are present;
- current user/session has required permissions or elevation;
- expected device identity is present if the pattern requires it;
- output evidence directory is writable;
- stale locks or conflicting monitor sessions are not blocking execution;
- signed request or operator confirmation is present for privileged/delegated operations.

Internal separation rationale:

| Dimension | `project validate` | `monitor preflight` |
| --- | --- | --- |
| Scope | Durable project config | One concrete monitor operation |
| Timing | Anytime | Immediately before execution |
| Volatility | Mostly stable | Highly volatile |
| Requires live device | Usually no | Often yes |
| Requires capture backend | Usually no | Yes when operation needs it |
| Failure meaning | Fix project/config | Operation cannot safely run now |

Example: the durable project checks can pass while the runtime readiness gate for `--pattern vulcan-s3-usbpcap` fails because USBPcap or TShark is missing. That is correct: the project is configured, but this host is not currently ready for that capture. The operator should not have to remember separate `project validate` or `monitor preflight` commands; ordinary monitor/test commands should run both classes of checks automatically.

### Current best candidate command flow

Superseding low-operator-load flow for a Vulcan S3 capture lane:

1. Optional durable default: `calamum project set calamum-vulcan`
2. Primary execution: `calamum monitor pcap capture --pattern vulcan-s3-usbpcap`
3. Evidence review: `calamum project evidence sessions show <session_id>`
4. Report generation: `calamum project evidence reports generate --scope job --job <task_id>`
5. Optional cleanup of durable default: `calamum project clear`

The primary execution command must internally resolve project context, validate project/preset enough for safety, run volatile readiness gates, prompt with evidence and choices when a conflict is safely resolvable, and execute only when all gates pass. The canonical noninteractive trigger is `--json`; with `--json`, conflict prompts are replaced by structured retained no-go packets with retry guidance.

Operational dependency note: the active Calamum Vulcan remediation job is blocked until this Calamum monitor scaffolding is operational enough to provide the native monitor command surface, automated readiness gates, retained no-go/capture packets, and project-scoped evidence lookup.

## Metadata

- Updated By: `ORACL-Prime`
- Last Transition (UTC): `2026-05-02T19:33:38.933033Z`
- Status Authority: `operations/tasks.json`
- Task ID: `calamum-job-0001-tools_gate_lifecycle-20260502`
- Status: `completed`
