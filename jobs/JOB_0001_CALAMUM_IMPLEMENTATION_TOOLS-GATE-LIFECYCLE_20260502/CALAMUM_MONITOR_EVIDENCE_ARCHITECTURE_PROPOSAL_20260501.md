TL;DR: Use three top-level Calamum families: `calamum test`, `calamum monitor`, and `calamum project`. Keep `test` focused on validation execution, make `monitor` the native monitoring/capture execution family, and make `project` own registration, active-project state, presets/config, and retained evidence. Favor one-command, low-operator-load execution such as `calamum monitor pcap capture --pattern vulcan-s3-usbpcap`; the orchestrator must automatically resolve project context, run required project/preset/readiness checks, prompt on resolvable conflicts, and retain evidence. PyShark, TShark, USBPcap, and similar tools remain internal monitor adapters only.

# Proposal: Calamum monitor and evidence command architecture

## 1. Status and authority posture

- Operator: `joediggidyyy`
- Planner: `ORACL-Prime`
- Date: `2026-05-01`
- Scope: architecture and process proposal only
- Implementation posture: no code changes authorized in this pass
- Artifact role: supporting proposal for later operator review and implementation planning

This document does not replace first-order CodeSentinel lifecycle authority. Current lifecycle authority remains:

- `docs/policies/operations/OPERATIONS_POLICY/PP_OPS_PROTOCOL_POL_JOB_PIPELINE_AUTHORITY_AND_EXECUTION_ARTIFACTS_20260312.md`
- `docs/operations/ssot/JOBS_AND_EXECUTION_SSOT.md`
- `operations/tasks.json`

If this proposal is later adopted as a required canonical path, the policy/SSOT edit targets listed in Section 11 must be updated in a separate authorized pass.

## 2. Executive recommendation

Create three clear Calamum top-level families:

| Family | Canonical responsibility | Notes |
| --- | --- | --- |
| `calamum test` | Test definition discovery and execution across `pytest`, `sandbox_test`, and `empirical_test` lanes. | Keep this focused on validation definitions and lane orchestration. |
| `calamum monitor` | Native monitoring, capture, instrumentation, and monitor-session orchestration. | Third-party tools are adapters, not command-family names; readiness checks are required internal stages, not extra user errands. |
| `calamum project` | Project registration, active-project state, project config/presets, and project-scoped retained evidence. | No `project manage` layer in the preferred shape; use direct verbs and resource families. |

Recommended naming decision: use `calamum project evidence`, not top-level `calamum evidence`, as the canonical retained-output family. Evidence is project-scoped because it resolves through `.calamum/project.json`, run/report roots, local overlays, project aliases, and future user-management trust context. `calamum report` remains too narrow because the requested scope includes report generation, evidence retrieval, file/artifact lookup, bundle creation, and verification. `calamum files` remains too storage-oriented and does not communicate provenance or trust. `project evidence` covers the retained-output lifecycle while allowing `reports` to exist as a subcommand.

Important operator-load rule: explicit validation/readiness commands should not be required in ordinary workflows. The orchestrator must run the same checks automatically and either proceed, fail closed, or present an interactive evidence-rich prompt when the conflict is safely resolvable.

## 3. Goals

1. Provide a native Calamum monitoring surface for host/device/runtime observations.
2. Ensure PyShark and related third-party capture tools are invoked only through Calamum adapters.
3. Make monitor outputs first-class retained evidence bundles with JSON-first records and Markdown companions.
4. Integrate monitor evidence with `calamum test` without forcing all monitoring to masquerade as test execution.
5. Move retained-run inspection and report generation out of `calamum test` into `calamum project evidence` while preserving compatibility aliases.
6. Preserve existing Calamum security posture: path containment, signed receipts/manifests where already supported, checksums, evidence retention, and future handoff to the v3 user-management/trust system.
7. Minimize operator load through named presets/patterns and automated gates while retaining explicit flags for deterministic automation.
8. Migrate Vulcan-specific monitoring scripts into reusable Calamum monitor orchestration.

## 4. Non-goals

- Do not expose `calamum monitor pyshark` or any equivalent backend-named command family.
- Do not require PyShark for ordinary Calamum test/report use.
- Do not claim TShark/Wireshark/USBPcap availability from a Python package install alone.
- Do not perform live device capture or host driver mutation without explicit operator authorization.
- Do not expose project-context readback, project validation, or monitor readiness checks as required manual steps for ordinary operators.
- Do not make every local, non-privileged monitor snapshot require a heavy signed request envelope.
- Do not remove existing `calamum test project`, `calamum test runs`, or `calamum test reports` immediately; migrate with compatibility aliases.
- Do not add user-facing `project trust` commands in this lane; trust/user/role management belongs to a later user-management system.
- Do not update CodeSentinel first-order authority files in the planning-only pass.

## 5. Command-family design

### 5.1 `calamum test` after this split

`calamum test` should remain the validation-definition execution surface.

Existing commands retained:

- `calamum test list`
- `calamum test show <definition_id>`
- `calamum test run <definition_id>`

Project registration and evidence inspection should no longer be canonical children of `test`. `calamum test project ...`, `calamum test runs ...`, and `calamum test reports ...` can remain transitional aliases, but the stable design should route those concerns through `calamum project`.

Recommended additions:

- `calamum test run <definition_id> --monitor-pattern <pattern_id>`
- `calamum test run <definition_id> --attach-evidence <evidence_ref>`
- `calamum test run <definition_id> --evidence-label <label>`
- `calamum test run <definition_id> --require-monitor-result <result_policy>`

Intended behavior:

- A test can require or attach a monitor pattern, but the actual monitoring execution is delegated to the shared monitor orchestrator.
- Retained output from both the test and monitor paths lands in the shared evidence store.
- Test reports cite monitor evidence by stable evidence references rather than copying ad hoc file paths.

Compatibility aliases:

- `calamum test project register ...` -> `calamum project register ...`
- `calamum test project set ...` -> `calamum project set ...`
- `calamum test runs list` -> `calamum project evidence runs list`
- `calamum test runs show <run_id>` -> `calamum project evidence runs show <run_id>`
- `calamum test reports list` -> `calamum project evidence reports list`
- `calamum test reports show <report_ref>` -> `calamum project evidence reports show <report_ref>`
- `calamum test reports generate ...` -> `calamum project evidence reports generate ...`

### 5.2 New `calamum monitor`

`calamum monitor` should own monitoring, capture, and instrumentation.

Recommended subcommand groups:

| Group | Purpose | Example shape |
| --- | --- | --- |
| `pnp` | Windows USB/PnP and host identity monitoring. | `calamum monitor pnp snapshot --json`; `calamum monitor pnp timeline --duration-seconds 30` |
| `pcap` | Packet/pcap capture and pcap file inspection. | `calamum monitor pcap interfaces --source usb`; `calamum monitor pcap capture --pattern vulcan-s3-usbpcap` |
| `session` | Multi-step monitor orchestration combining captures, prompts, diagnostics, and rollups. | `calamum monitor session run --pattern vulcan-gui-pit-session --job <task_id>` |
| `capability` | Optional advanced/debug readback of supported monitor adapters; ordinary capture commands run readiness gates automatically. | `calamum monitor capability list --json` |

Important naming rule:

- Good: `calamum monitor pcap capture --source usb --pattern vulcan-s3-usbpcap`
- Good: `calamum monitor pnp timeline --pattern vulcan-pnp-timeline`
- Best low-overhead path: `calamum monitor pcap capture --pattern vulcan-s3-usbpcap`
- Avoid: `calamum monitor pyshark ...`
- Avoid: `calamum monitor tshark ...`
- Avoid: `calamum monitor usbpcapcmd ...`

Third-party backend names may appear in retained machine-readable adapter metadata and automated readiness details, but they should not be the primary operator command family.

Monitor commands must internally run the required orchestration gates: project resolution, project config sanity checks, preset/pattern expansion, runtime readiness checks, permission checks, output-root checks, and conflict handling. These checks are mandatory engine stages, not optional user responsibilities.

### 5.3 New top-level `calamum project`

`calamum project` should become the canonical context family. It should own project registration/default state, project config/presets, and project-scoped evidence retrieval/reporting.

Recommended direct project commands:

- `calamum project register`
- `calamum project set <project>`
- `calamum project clear`
- `calamum project list`
- `calamum project show <project>`

`project set` persists a default active-project pointer in the Calamum user config state. It does not start a runtime session and does not require an end command. `project clear` removes that persistent default pointer. Ordinary commands should still prefer explicit `--project`, nearest `.calamum/project.json`, and `CALAMUM_PROJECT` before falling back to the persistent default.

`project current` and `project validate` should not be required operator workflow steps. Their underlying functions should be absorbed into the orchestrator. If retained at all, they should be diagnostic/readback aliases for advanced users, not documented as ordinary prerequisites.

Recommended project resource families:

| Group | Purpose | Example shape |
| --- | --- | --- |
| `config` | Inspect or modify project descriptor/local overlay settings. | `calamum project config show`; `calamum project config set <key> <value>` |
| `presets` | Manage named reusable execution presets for tests and monitors. | `calamum project presets list`; `calamum project presets show vulcan-s3-usbpcap` |
| `evidence` | Retrieve, verify, report, bundle, export, and index retained evidence for the resolved project. | `calamum project evidence runs list`; `calamum project evidence reports generate --scope job --job <task_id>` |

Recommended `project evidence` commands:

Recommended subcommand groups:

| Group | Purpose | Example shape |
| --- | --- | --- |
| `runs` | List/show retained test runs. | `calamum project evidence runs list`; `calamum project evidence runs show <run_id>` |
| `sessions` | List/show retained monitor sessions. | `calamum project evidence sessions list`; `calamum project evidence sessions show <session_id>` |
| `reports` | Generate/show/list aggregate reports. | `calamum project evidence reports generate --scope job --job <task_id> --sign` |
| `bundle` | Create portable evidence bundles from runs/sessions/reports. | `calamum project evidence bundle create --ref <evidence_ref>` |
| `verify` | Verify checksums, manifests, receipts, and signatures. | `calamum project evidence verify <evidence_ref> --strict` |
| `index` | Inspect/rebuild local evidence indices. | `calamum project evidence index list`; `calamum project evidence index rebuild --scope project` |
| `export` | Export evidence in controlled forms for review or transfer. | `calamum project evidence export <evidence_ref> --format zip --sign` |

This family should consume the current `runner.py` and `reports.py` functionality after extraction, so reports and retained-run inspection are not stranded under the `test` namespace.

The proposal now rejects `catalog`, side-by-side `definitions`, and side-by-side `patterns` as primary user-facing management nouns. Use `project presets` as the unified management surface for reusable execution recipes. Internally, a preset can still have a `kind` such as `test` or `monitor`, and monitor execution can still use the intuitive `--pattern` flag.

## 6. Shared engine architecture

### 6.1 Current reusable primitives

Existing Calamum files already provide the base:

- `projects/calamum/src/calamum/runner.py`
  - command execution, stdout/stderr capture, run directories, manifests, checksums, run index.
- `projects/calamum/src/calamum/reports.py`
  - report generation, receipt emission, optional signatures, report index, report history.
- `projects/calamum/src/calamum/projects.py`
  - project context, local overlays, active-project state, path aliases, containment, and existing trust metadata that should be routed through a future user-management system before becoming user-facing.
- `projects/calamum/src/calamum/signing.py`
  - canonical JSON signing, signature verification, checksum sidecars.
- `projects/calamum/src/calamum/api.py`
  - stable facade for host applications.

### 6.2 Proposed extraction shape

Future implementation should separate orchestration from test-specific naming:

| Proposed component | Extracted or new responsibility |
| --- | --- |
| `calamum.orchestrator` | Generic step/session orchestration, heartbeat, output capture, error handling, artifact registration. |
| `calamum.project.evidence` or `calamum.evidence` internals | Shared evidence bundle model, indices, show/list/verify/export APIs exposed through `calamum project evidence`. |
| `calamum.test` | Test preset execution using the shared orchestrator. |
| `calamum.monitor` | Monitor pattern expansion and monitor-session execution using the shared orchestrator. |
| `calamum.project` | Project descriptor, overlay, active-state, config, preset management, and conflict-resolution prompts exposed through direct `calamum project ...` commands. |
| `calamum.reports` | Report rendering and aggregate generation, relocated under project-evidence-facing command routes while preserving import compatibility. |

The goal is not to fork a second runner for monitoring. The goal is one retained-evidence engine that can execute test lanes and monitor sessions with different front doors.

### 6.3 Evidence object model

Recommended shared evidence reference model:

| Field | Meaning |
| --- | --- |
| `schema_version` | Versioned evidence schema, such as `calamum-evidence-bundle-v1`. |
| `evidence_id` | Stable unique bundle id. |
| `kind` | `test_run`, `monitor_session`, `aggregate_report`, `export_bundle`, or future value. |
| `project_id` | Resolved Calamum project id. |
| `domain` | Project/domain classification. |
| `job_id` | Optional job/task id. |
| `created_at` | UTC timestamp. |
| `source_family` | `test`, `monitor`, or `project_evidence`. |
| `preset_id` | Optional reusable execution preset id. |
| `decision` | `go`, `no-go`, `blocked`, `planned`, or similar. |
| `result` | Domain result such as `pass`, `failed`, `captured`, `blocked`, `inconclusive`. |
| `artifacts` | Named artifact paths. |
| `manifest` | Manifest path/reference. |
| `checksums` | Checksum manifest or sidecars. |
| `signatures` | Detached signatures where present. |
| `next_review_command` | Native command for reopening the evidence. |

This schema should wrap the current test run report shape without breaking it, then extend naturally to monitor sessions.

## 7. Preset/config model

### 7.1 Preset roots

Recommended split:

| Storage | Purpose |
| --- | --- |
| tracked project preset library, for example `.calamum/presets/*.json` or a compatibility bridge to the existing test-definition store | Project-shared reusable test and monitor recipes. |
| user config root, for example `%APPDATA%/Calamum/presets/<project_id>.local.json` | Machine-local overlays such as local interface ids, capture backend preferences, or host-specific paths. |
| `.calamum/project.json` | Project-level roots, default preset ids, retained-output roots, and safe aliases. |
| `.calamum/generated/...` | Local-only retained evidence outputs. |

Use a single tracked JSON file while the preset library is small. Move to split files plus an index when scale requires it. Avoid `catalog` as an operator-facing noun even if existing internal compatibility files retain that historical name.

### 7.2 Preset schema sketch

Recommended minimal preset fields:

| Field | Meaning |
| --- | --- |
| `id` | Stable exact-name preset id. |
| `title` | Human-facing title. |
| `status` | `active`, `experimental`, `deprecated`, or `disabled`. |
| `kind` | `test`, `monitor`, or future value. |
| `execution_type` | For monitor presets: `pnp`, `pcap`, `session`, `vulcan_pit`, or future type. For test presets: existing test lane/type metadata. |
| `profiles` | `smoke`, `release`, `nightly`, `s3`, etc. |
| `tags` | `usb`, `pcap`, `windows`, `vulcan`, `pit`, `retained-evidence`. |
| `policy_flags` | `json-first`, `containment`, `privileged-operation`, `signed-output`, `local-only`, `operator-confirmation`. |
| `requirements` | Backend/capability requirements such as TShark presence or USB capture support. |
| `defaults` | Sample intervals, duration, source, filters, output mode. |
| `evidence_requirements` | Required artifacts and verification outputs. |
| `steps` | Ordered monitor/orchestration steps for session patterns. |
| `security` | Confirmation, containment, and future user-management hooks. |
| `reporting` | Auto-generate report/bundle settings. |

### 7.3 Preset management commands

Recommended commands:

- `calamum project presets list [--kind test|monitor]`
- `calamum project presets show <preset_id>`
- `calamum project presets scaffold <preset_id> --kind test|monitor`
- `calamum project presets add --from-file <path> [--local|--tracked]`
- `calamum project presets explain-schema`
- `calamum project presets disable <preset_id> --reason <reason>`

`add --tracked` should be explicit because it changes project-shared preset inputs. `add --local` is the safer default for host-specific interface details. Validation still happens, but it should run automatically during add/scaffold/edit and again during execution; the user should not need to remember a separate `validate` command.

### 7.4 Recommended first Vulcan presets

| Preset id | Purpose | Maps from current script |
| --- | --- | --- |
| `vulcan-pnp-snapshot` | Capture one Windows USB/PnP token/owner snapshot. | `run_pit_transport_diagnostic.py::_collect_windows_usb_snapshot` |
| `vulcan-pnp-timeline` | Capture repeated Windows USB/PnP timeline while the operator performs PIT action. | `run_gui_pit_continuous_monitor.py` |
| `vulcan-pit-transport-diagnostic` | Run deterministic PIT parser/fallback matrix and optional live PIT diagnostic. | `run_pit_transport_diagnostic.py` |
| `vulcan-gui-pit-session` | Run monitor timeline, wait/auto-finalize around GUI action, then run post-GUI diagnostic. | `run_gui_pit_evidence_session.py` |
| `vulcan-s3-usbpcap` | Run S3 USB packet-capture discriminator through pcap adapter with automated readiness gates and retained capture metadata. | New pcap monitor path using PyShark/TShark/USBPcap adapters internally. |

## 8. PyShark, TShark, Wireshark, and USBPcap integration policy

### 8.1 Dependency roles

| Component | Role | Packaging implication |
| --- | --- | --- |
| PyShark | Python wrapper/orchestration library for TShark. | Optional Calamum monitor dependency, not required for base `calamum-test`. |
| TShark/Wireshark | System packet analysis/capture backend. | Must be discovered by automated readiness gates; cannot be installed or assumed by pip alone. |
| dumpcap | Capture helper often installed with Wireshark. | Readiness gates should record presence/version/capabilities. |
| USBPcap | Windows USB capture backend/driver/tooling. | Readiness gates should record presence, privileges, interface list, and whether capture is possible. |

### 8.2 Invocation rule

Operators and downstream applications must invoke monitoring through Calamum:

- allowed: `calamum monitor pcap capture --pattern vulcan-s3-usbpcap`
- allowed: `calamum.monitor.run_pattern("vulcan-s3-usbpcap", ...)` through the Python API
- not allowed: direct operator use of PyShark, TShark, dumpcap, USBPcapCMD, or backend-specific scripts as the canonical evidence path

Direct backend use can remain a troubleshooting escape hatch only if explicitly authorized and recorded as noncanonical evidence.

### 8.3 Automated readiness-gate behavior

Every monitor execution should run an internal readiness gate and retain a capability packet with:

- OS/platform;
- Python package presence for optional adapters;
- TShark path/version when available;
- dumpcap path/version when available;
- USBPcap presence and interface enumeration when available;
- privilege/elevation status when detectable;
- whether capture is possible, blocked, unsupported, or inconclusive;
- exact reason for no-go outcomes;
- next native Calamum command to retry or inspect evidence.

If TShark/USBPcap are missing, the command should fail closed with a clear no-go packet. It must not pretend that PyShark alone satisfies live USB capture readiness.

Interactive conflict handling should use a polished prompt that shows evidence first and choices second. Example conflicts include multiple plausible project contexts, missing optional local overlay values, non-default capture interfaces, and privilege/elevation uncertainty. The canonical noninteractive trigger is `--json`: when `--json` is present, the same condition should produce a structured no-go packet with candidate choices and the exact flag or project setting needed to retry, rather than prompting.

## 9. Security and governance model

### 9.1 Security tiers

| Tier | Example monitor action | Required controls |
| --- | --- | --- |
| Tier 1: local passive observation | `pnp snapshot`, read-only timeline capture | Retained evidence bundle, manifest/checksum, path containment, no secrets in outputs. |
| Tier 2: privileged local capture | USB packet capture, interface enumeration requiring elevated access | Operator confirmation when needed, automated readiness gate, retained receipt, manifest/checksum, optional signatures. |
| Tier 3: delegated/cross-application monitor request | CodeSentinel or Vulcan asks Calamum to run official S3 capture | Defer user/requester trust, roles, requester allowlists, nonce/replay policy, and delegated identities to the future user-management system. |

### 9.2 User-management deferral

Do not add user-facing `calamum project trust ...` commands in this lane. The needed functions are real, but they belong to a not-yet-conceived user-management system and should be treated as v3 scope.

For current planning, the monitor/evidence engine should expose narrow internal hooks where that future system can later answer questions such as:

- who is requesting this capture;
- whether the requester has permission for privileged capture;
- whether delegated evidence is publishable;
- which signatures/receipts are required;
- whether an interactive confirmation can be skipped.

Until then, local flows should use operator confirmation, environment/config containment, manifests, checksums, and existing signature helpers where already available. Avoid inventing a half-trust CLI that will need to be removed when the user-management model arrives.

### 9.3 Containment and data hygiene

The monitor engine should enforce:

- no writes outside declared runs/reports/evidence roots;
- no secrets in shared presets or `.calamum/project.json`;
- machine-local capture backend paths in local overlays only;
- public reports use project-relative paths or safe path tails, not unredacted host-specific absolute paths;
- external command displays are sanitized so secrets and local tokens are not leaked;
- monitor adapters must record backend metadata but should avoid exposing raw backend command strings as the primary operator contract.

## 10. Vulcan migration plan

### 10.1 Current-to-future mapping

| Current Vulcan script/function | Future Calamum route | Notes |
| --- | --- | --- |
| `tools/run_gui_pit_continuous_monitor.py::_capture_sample` | `calamum monitor pnp snapshot` API and adapter | Preserve token extraction and owner mapping. |
| `tools/run_gui_pit_continuous_monitor.py` main loop | `calamum monitor pnp timeline` | Retain sample interval/duration/annotation flags. |
| `tools/run_pit_transport_diagnostic.py::_collect_windows_usb_snapshot` | shared Windows PnP adapter | Avoid duplicate PowerShell snapshot code. |
| `tools/run_pit_transport_diagnostic.py::build_pit_transport_summary` | `calamum monitor session run --pattern vulcan-pit-transport-diagnostic` | Keep deterministic matrix plus optional live commands. |
| `tools/run_gui_pit_evidence_session.py` | `calamum monitor session run --pattern vulcan-gui-pit-session` | Preserve GUI action window, auto-finalize, post-diagnostic, rollup, and next-action output. |
| future S3 capture | `calamum monitor pcap capture --pattern vulcan-s3-usbpcap` | New adapter path; PyShark/TShark/USBPcap hidden behind native command. |

### 10.2 Transitional strategy

1. Implement Calamum monitor adapters and automated readiness gates first.
2. Add Vulcan monitor presets under a project-owned Calamum preset library or a Calamum application-profile extension.
3. Preserve current Vulcan scripts as thin wrappers that print the new native Calamum command and optionally dispatch to the API only during transition.
4. Mark direct script invocation as noncanonical after native commands are proven.
5. Update Vulcan docs so S3 evidence must use `calamum monitor` and retained evidence must be retrieved through `calamum project evidence`.
6. Retire or archive old script-only flows only after the native path has equal or better evidence coverage.

### 10.3 Vulcan S3 command examples

Proposed native shapes:

- `calamum project set calamum-vulcan`
- `calamum monitor pcap capture --pattern vulcan-s3-usbpcap --job calamum-vulcan-job-0001-docs_remediation_planning-20260501 --json`
- `calamum monitor pnp timeline --pattern vulcan-pnp-timeline --job calamum-vulcan-job-0001-docs_remediation_planning-20260501 --json`
- `calamum monitor session run --pattern vulcan-gui-pit-session --job calamum-vulcan-job-0001-docs_remediation_planning-20260501 --json`
- `calamum project evidence sessions show <session_id> --json`
- `calamum project evidence reports generate --scope job --job calamum-vulcan-job-0001-docs_remediation_planning-20260501 --sign --json`
- `calamum project clear`

The actual implementation should refine flag names, but the important contract is that the operator invokes Calamum-native monitor/evidence surfaces, not external tools directly. Project resolution, preset validation, readiness checks, and evidence retention happen inside each monitor command. If conflict resolution is needed, the command prompts with evidence and choices; when `--json` is present, it fails closed with a retained no-go packet instead of prompting.

Current execution dependency: the active Calamum Vulcan remediation job should remain blocked until the Calamum monitor scaffolding is operational enough to provide the native monitor command surface, automated readiness gates, retained no-go/capture packets, and project-scoped evidence retrieval described here. Continuing Vulcan live PIT/S3 remediation before this scaffold exists would risk another visibility-only rerun instead of approval-grade evidence.

## 11. Required policy, governance, and support edit targets

No code, policy, support-doc, or implementation edits beyond this proposal update are authorized in this planning pass. The following are candidate future edit targets if the operator approves implementation and canonical-path elevation.

### 11.1 Calamum package/product docs

| Target | Required future update |
| --- | --- |
| `projects/calamum/README.md` | Document top-level `monitor` and `project`; move report/run inspection docs out of `test` into `project evidence` as canonical; keep compatibility notes. |
| `projects/calamum/SECURITY.md` | Add monitor-specific privilege/capture policy, automated readiness gates, retained receipts/manifests, user-management deferral, and no-direct-tooling rule. |
| `projects/calamum/planning/CALAMUM_TEST_CHILD_REPO_IMPLEMENTATION_PLAN_20260423.md` | Add an implementation addendum for monitor/evidence split if accepted into current scope. |
| `projects/calamum/planning/CALAMUM_TEST_V2_TARGETS_20260423.md` | Clarify whether monitor/evidence is current implementation or v2 silent integration; avoid accidental scope drift. |
| future `projects/calamum/docs/monitoring.md` | New support doc for monitor patterns/presets, backend requirements, automated readiness gates, and examples. |
| future `projects/calamum/docs/evidence.md` | New support doc for evidence references, bundles, verification, reports, and compatibility aliases. |
| future `projects/calamum/docs/preset-schema.md` | New support doc for preset schema and local overlays. |

### 11.2 Calamum code/API edit targets

| Target | Required future update |
| --- | --- |
| `projects/calamum/src/calamum/cli.py` | Add top-level `monitor` and `project`; route retained outputs through `project evidence`; retain aliases from `test runs/reports`. |
| `projects/calamum/src/calamum/api.py` | Export monitor/evidence APIs for host applications. |
| `projects/calamum/src/calamum/runner.py` | Extract generic orchestration pieces or wrap them from a new shared orchestrator module. |
| `projects/calamum/src/calamum/reports.py` | Route report generation through `project evidence` namespace while preserving import compatibility. |
| `projects/calamum/src/calamum/catalog.py` or successor | Bridge existing test-definition storage into the user-facing preset model without exposing `catalog` as the operator noun. |
| `projects/calamum/src/calamum/projects.py` | Add monitor/evidence roots and local overlay support if needed. |
| `projects/calamum/src/calamum/signing.py` | Keep existing helpers available for receipts/manifests; avoid adding user-facing trust commands in this lane. |
| future `projects/calamum/src/calamum/monitor/*` | Implement monitor adapters, sessions, patterns, and automated readiness gates. |
| future `projects/calamum/src/calamum/evidence.py` | Implement shared evidence listing, showing, bundle/export, verify, and index operations. |
| `projects/calamum/pyproject.toml` | Add optional monitor dependencies such as a `[project.optional-dependencies] monitor = [...]` group if PyShark is adopted. |

### 11.3 Calamum tests

| Target | Required future validation |
| --- | --- |
| `projects/calamum/tests/test_cli.py` | Add help/JSON parity tests for `monitor` and `project evidence`; alias tests for old `test runs/reports`. |
| future `projects/calamum/tests/test_monitor_*.py` | Validate preset/pattern parsing, automated readiness no-go packets, pnp snapshot normalization, pcap adapter fail-closed behavior. |
| future `projects/calamum/tests/test_evidence_*.py` | Validate evidence refs, bundle creation, verify, index rebuild, report migration. |
| future integration tests | Prove `calamum test run --monitor-pattern ...` attaches monitor evidence without path escapes. |

### 11.4 Calamum Vulcan docs and scripts

| Target | Required future update |
| --- | --- |
| `projects/calamum-vulcan/docs/Samsung_Android_Flashing_Platform_0.6.0_Testing_and_Readiness_Plan.md` | Require native Calamum monitor/project-evidence routes for future PIT/S3 evidence. |
| `projects/calamum-vulcan/docs/operations/FRAME_STACK_PHASED_REMEDIATION_EXECUTION_2026-04-26.md` | Replace direct S3 tooling instructions with `calamum monitor` paths and waiver language. |
| `projects/calamum-vulcan/docs/operations/Sprint_0.6.0_Round_Log.md` | Record transition from local scripts to Calamum monitor/project-evidence once implemented. |
| `projects/calamum-vulcan/tools/run_gui_pit_*.py` | Migrate logic into Calamum monitor adapters; leave wrappers only during transition. |
| Vulcan Calamum project descriptor/preset library | Add Vulcan monitor presets/pattern ids and evidence roots once project-specific registration is defined. |

### 11.5 CodeSentinel authority docs, only if canonical usage is elevated

Use caution: these are first-order or near-first-order routing surfaces. Edit only in a separately authorized pass.

| Target | Required future update if elevated |
| --- | --- |
| `docs/policies/operations/OPERATIONS_POLICY/PP_OPS_PROTOCOL_POL_JOB_PIPELINE_AUTHORITY_AND_EXECUTION_ARTIFACTS_20260312.md` | Define when `calamum project evidence` is canonical for retained validation/evidence reports. |
| `docs/operations/ssot/JOBS_AND_EXECUTION_SSOT.md` | Align job close/report evidence routing with `calamum project evidence` if required. |
| `operations/tasks.json` task metadata | Add deterministic contracts only for lanes that require monitor/evidence aggregation. |
| `codesentinel/assets/VAULT_templates/jobpipeline/JOB_CREATE.*.template` | Update validation evidence text if `calamum project evidence` replaces `calamum test reports` wording. |
| CodeSentinel close-path code/tests | Update only if close manifests must reference `calamum project evidence` outputs rather than current `calamum.api.generate_report` behavior. |

## 12. Implementation phases

### Phase 0 - design freeze and schema review

Deliverables:

- confirm `calamum test`, `calamum monitor`, and `calamum project` as the only top-level families in this lane;
- confirm `--json` as the canonical noninteractive trigger for no-prompt structured decisions;
- freeze command naming rules;
- define evidence bundle schema;
- define preset schema and monitor pattern semantics;
- decide optional dependency strategy for PyShark.

Validation:

- no code required;
- operator sign-off on command grammar and canonical-path split.

### Phase 1 - project evidence extraction

Deliverables:

- add `calamum project evidence runs list/show`;
- add `calamum project evidence reports list/show/generate`;
- preserve `calamum test runs/reports` as compatibility aliases;
- keep output payload parity with current commands.

Validation:

- CLI help tests;
- JSON parity tests between alias and canonical route;
- existing report generation tests unchanged or updated with aliases.

### Phase 2 - evidence bundle/verify/export foundation

Deliverables:

- shared evidence reference model;
- `calamum project evidence verify` for manifests/checksums/signatures;
- `calamum project evidence bundle create`;
- `calamum project evidence index list/rebuild`.

Validation:

- checksum tamper tests;
- missing artifact no-go tests;
- bundle manifest tests;
- public path redaction tests.

### Phase 3 - passive monitor foundation

Deliverables:

- `calamum monitor capability list`;
- `calamum monitor pnp snapshot`;
- `calamum monitor pnp timeline`;
- automated project/preset/readiness gates inside monitor execution;
- monitor session artifacts retained as evidence bundles.

Validation:

- Windows/non-Windows behavior tests;
- no-go tests for unsupported platform;
- fake snapshot parser tests;
- evidence retention tests.

### Phase 4 - preset library

Deliverables:

- `calamum project presets list/show/scaffold/add/explain-schema`;
- tracked preset library plus local overlay support;
- preset expansion into explicit command parameters;
- single-parameter pattern execution.

Validation:

- duplicate id and vocabulary tests;
- local overlay merge tests;
- disabled/deprecated pattern no-go behavior;
- no secrets in shared preset fixture tests.

### Phase 5 - pcap adapter and S3 readiness gate

Deliverables:

- optional PyShark adapter import;
- TShark/dumpcap/USBPcap capability discovery;
- `calamum monitor pcap interfaces`;
- `calamum monitor pcap capture` with no direct backend exposure;
- fail-closed automated readiness gate when required system tooling is absent.

Validation:

- missing PyShark no-go;
- PyShark installed but TShark missing no-go;
- USBPcap missing no-go on Windows USB capture pattern;
- operator-confirmation/privileged capture tests, with v3 trust integration deferred.

### Phase 6 - Vulcan migration

Deliverables:

- Vulcan PnP and PIT diagnostic adapters;
- Vulcan monitor presets/pattern ids;
- `vulcan-gui-pit-session` monitor session;
- S3 USBPcap capture pattern;
- thin transitional wrappers or deprecation notices for old scripts.

Validation:

- fixture-based PIT diagnostic parity tests;
- retained evidence output parity with current scripts;
- no direct external command in user-facing invocation tests;
- Vulcan docs updated to cite native Calamum commands.

### Phase 7 - test integration

Deliverables:

- `calamum test run --monitor-pattern <id>`;
- test run report includes monitor evidence refs;
- aggregate reports include attached monitor sessions;
- close-path downstream consumers can reference evidence bundles.

Validation:

- test plus monitor dry-run tests;
- monitor failure blocks or annotates test result according to policy;
- aggregate report includes test and monitor evidence.

### Phase 8 - governance and release hardening

Deliverables:

- README/security/docs updates;
- CodeSentinel policy/SSOT updates if canonical elevation is approved;
- optional dependency packaging;
- standalone repo sync hygiene;
- release notes and migration guide.

Validation:

- full `calamum test` suite;
- CodeSentinel governed lane validation where relevant;
- secret scanning of new docs/config examples;
- alias deprecation behavior verified.

## 13. Acceptance criteria

A future implementation should not be considered complete until:

1. `calamum monitor` exists as a top-level family and exposes no backend-named command family.
2. `calamum project evidence` exists as the canonical family for run/session/report retrieval and verification.
3. Existing `calamum test runs/reports` routes continue to work as aliases or documented compatibility paths.
4. Monitor sessions write retained JSON/Markdown/manifest/checksum evidence packs.
5. Privileged capture operations run automated readiness gates and require confirmation according to tier.
6. PyShark absence, TShark absence, and USBPcap absence each produce accurate fail-closed packets.
7. Vulcan's current GUI/PIT evidence session can be executed as a native Calamum monitor pattern/preset.
8. Aggregate reports can include or cross-reference monitor evidence bundles.
9. The docs state clearly that direct PyShark/TShark/USBPcap invocation is noncanonical for governed evidence.
10. Code changes are validated through `calamum test` according to the repository validation memory, with narrower tests only as supplemental evidence.
11. Ordinary monitor/test commands automatically run context resolution, project checks, preset expansion, and readiness gates; users are not required to run `project current`, `project validate`, or `monitor preflight` first.
12. With `--json`, interactive conflict prompts are suppressed and replaced by structured go/no-go packets with candidate choices and retry guidance.

## 14. Risks and mitigations

| Risk | Mitigation |
| --- | --- |
| PyShark installed but TShark/USBPcap missing | Automated readiness gates must test backend availability and fail closed. |
| Operator sees backend names and bypasses Calamum | Keep backend names out of primary command families; docs must state native paths are canonical. |
| Evidence paths leak host-specific details | Use project-relative references and safe path tails in public reports. |
| `project evidence` split breaks existing users | Keep compatibility aliases and JSON payload parity during migration. |
| Preset files become secret sinks | Shared presets must reject secrets and host-specific credentials; local overlays carry host-specific nonsecret settings. |
| Monitor capture requires elevation | Treat capture as privileged; require confirmation when needed and retain receipts/no-go packets. |
| Scope drift into full remote trust fabric | Keep remote/delegated mesh out of this lane unless separately elevated. |
| Vulcan-specific logic pollutes generic Calamum core | Put generic PnP/pcap primitives in Calamum core; put Vulcan PIT semantics behind patterns/adapters. |

## 15. Recommended immediate next action

If the operator accepts this proposal, open a new implementation lane with the following first frame:

1. add `calamum project evidence` routes for existing run/report commands;
2. add tests proving output parity with `calamum test runs/reports`;
3. add `calamum project set` and `calamum project clear` around the existing active-state machinery;
4. define the monitor scaffolding minimum viable slice: command shell, preset resolution, automated readiness gate, `--json` no-prompt no-go packets, retained evidence packet, and project evidence lookup;
5. document the migration path in `projects/calamum/README.md` and `projects/calamum/SECURITY.md`;
6. keep the active Calamum Vulcan remediation job blocked until the monitor scaffolding minimum viable slice is operational.

Reason: project evidence plus `project set/clear` is the cleanest low-risk first step. It separates reporting/retrieval from test execution, proves the top-level `project` family, and prepares the low-overhead monitor path before adding the more sensitive capture stack. The Vulcan lane should wait on that scaffold because the requested S3/PIT evidence flow now depends on Calamum-native monitor orchestration rather than direct project-local scripts.

## Metadata

- Updated By: `ORACL-Prime`
- Last Transition (UTC): `2026-05-02T19:33:38.933033Z`
- Status Authority: `operations/tasks.json`
- Task ID: `calamum-job-0001-tools_gate_lifecycle-20260502`
- Status: `completed`
