TL;DR: This audit-only pass confirms the planning-session authority model that `operations/tasks.json` remains the source of truth for state, while `QS.json` remains the source of truth for operational specifics not stored in `operations/tasks.json` and must never override state truth already held there. The broader investigation surfaced additional hierarchy gaps beyond cwd-sensitive lookup: runtime scaffold/governance strings in `jobs_utils.py` still describe `QS.json` too broadly, derived reader projections still overstate `QS.json` as sole truth in places where the hierarchy should be layered, and the current handler structure still does not express a clean state-first / operational-detail-second read model. The primary implementation defect remains the path-resolution issue in the `job frame` handlers, but the larger planning conclusion is that hierarchical truth sourcing is not yet fully realized or consistently propagated through the authority stack.

# Calamum Job Pipeline SSOT Audit Scratchpad

## Audit identity

- Audit date: `2026-05-02`
- Audit posture: `audit-only / no code changes / no lifecycle mutation requested beyond observed operator actions`
- Active lane under review: `calamum-job-0001-tools_gate_lifecycle-20260502`
- Job root: `projects/calamum/jobs/JOB_0001_CALAMUM_IMPLEMENTATION_TOOLS-GATE-LIFECYCLE_20260502`
- Auditor: `ORACL-Prime`
- Stakeholder: `joediggidyyy`

## Purpose

Execute a focused audit of the full job pipeline for the active Calamum lane and verify that, at every stage, truth remains anchored to the canonical SSOT surfaces rather than drifting into cwd-dependent lookups, stale projections, SessionMemory mirrors, or historical paperwork.

For this planning conversation, the operator clarification to preserve in this scratchpad is:

- `operations/tasks.json` is the only source of truth for job state.
- `operations/tasks.json` is the source of truth for state only.
- `QS.json` is an operational execution artifact that supplies additional frame-execution detail not held in `operations/tasks.json`.
- `QS.json` supplements `operations/tasks.json`; it does not override any truth already held in `operations/tasks.json`.

This audit is investigative only. It does not claim remediation, does not authorize code edits, and does not elevate this scratchpad to first-order execution authority.

## Project-goal context

The audited job exists to prepare the standalone `projects/calamum` monitor/project-evidence implementation lane for safe execution. The job's execution plan is explicitly planning-first and decomposed into a seven-frame stack that maps:

- authoritative planning corpus and command grammar,
- current Calamum substrate and compatibility boundaries,
- project-evidence retention and routing contracts,
- monitor/readiness/no-go contracts,
- downstream Vulcan consumer boundaries,
- minimum viable implementation slice and validation plan,
- execution-ready handoff packaging.

Because this lane is explicitly built around a repaired frame-stack model, the correctness of the job pipeline matters directly: if start/scaffold/frame commands disagree about where truth lives, the job cannot safely execute its planning program.

## Current authority lives in

Per the active first-order authority corpus, current execution authority lives in:

1. `operations/tasks.json`
2. `docs/operations/ssot/JOBS_AND_EXECUTION_SSOT.md`
3. `docs/policies/operations/OPERATIONS_POLICY/PP_OPS_PROTOCOL_POL_JOB_PIPELINE_AUTHORITY_AND_EXECUTION_ARTIFACTS_20260312.md`

Additional operational execution artifact after `job start`:

- `projects/calamum/jobs/JOB_0001_CALAMUM_IMPLEMENTATION_TOOLS-GATE-LIFECYCLE_20260502/QS.json`

Required derived projection under the repaired frame-stack model:

- `projects/calamum/jobs/JOB_0001_CALAMUM_IMPLEMENTATION_TOOLS-GATE-LIFECYCLE_20260502/QF.md`

Non-authoritative supporting/derived/runtime surfaces reviewed during this audit:

- `JOB.json`
- `JOB.md`
- `JOB.md.resolution_trace.json`
- `.agent_session/task_stack.json`
- `.agent_session/queststack_journal.jsonl`
- `logs/behavioral/jobs/job_events.jsonl`

## Corpus ingested for this audit

### First-order governance / SSOT corpus

- `docs/operations/ssot/JOBS_AND_EXECUTION_SSOT.md`
- `docs/policies/operations/OPERATIONS_POLICY/PP_OPS_PROTOCOL_POL_JOB_PIPELINE_AUTHORITY_AND_EXECUTION_ARTIFACTS_20260312.md`
- `operations/tasks.json`
- `.github/instructions/execution-authority.instructions.md`

### Active-lane planning / execution corpus

- `projects/calamum/jobs/JOB_0001_CALAMUM_IMPLEMENTATION_TOOLS-GATE-LIFECYCLE_20260502/JOB.json`
- `projects/calamum/jobs/JOB_0001_CALAMUM_IMPLEMENTATION_TOOLS-GATE-LIFECYCLE_20260502/JOB.md`
- `projects/calamum/jobs/JOB_0001_CALAMUM_IMPLEMENTATION_TOOLS-GATE-LIFECYCLE_20260502/QS.json`
- `projects/calamum/jobs/JOB_0001_CALAMUM_IMPLEMENTATION_TOOLS-GATE-LIFECYCLE_20260502/QF.md`
- `projects/calamum/jobs/JOB_0001_CALAMUM_IMPLEMENTATION_TOOLS-GATE-LIFECYCLE_20260502/CALAMUM_MONITOR_EVIDENCE_ARCHITECTURE_PROPOSAL_20260501.md`
- `projects/calamum/jobs/JOB_0001_CALAMUM_IMPLEMENTATION_TOOLS-GATE-LIFECYCLE_20260502/CALAMUM_MONITOR_EVIDENCE_ARCHITECTURE_SCRATCHPAD_20260501.md`
- `projects/calamum/planning/CALAMUM_TEST_CHILD_REPO_IMPLEMENTATION_PLAN_20260423.md`
- `projects/calamum/planning/CALAMUM_TEST_V2_TARGETS_20260423.md`
- `projects/calamum/.calamum/project.json`
- `projects/calamum/pyproject.toml`

### Pipeline implementation corpus

- `codesentinel/cli/job_utils.py`
- `codesentinel/cli/jobs_utils.py`
- `codesentinel/utils/workspace_root.py`
- `codesentinel/utils/ops_tasks_registry.py`

## Affected systems and project-goal map

The active lane is not an abstract paperwork exercise. It exists to prepare standalone Calamum for:

- a stable top-level command grammar (`calamum test`, `calamum project`, `calamum monitor`),
- project-scoped retained evidence and report routing,
- monitor/readiness/no-go packet design,
- safe downstream consumption by Calamum Vulcan without letting Vulcan become command authority.

That means the job/frame authority stack has to support planning rigor as well as runtime clarity:

1. `operations/tasks.json` must remain the canonical state surface.
2. `QS.json` must remain a supplemental execution artifact for richer frame narrative, carry-in tasks, evidence routes, validation summaries, and other operational detail not stored in `operations/tasks.json`.
3. `QF.md`, `JOB.md`, SessionMemory mirrors, and logs must present that hierarchy clearly enough that later implementation planning does not reintroduce authority drift.

Because this Calamum lane is explicitly planning-first and decomposed into seven frames, any ambiguity in hierarchical truth sourcing directly threatens the job's stated goal of producing an execution-ready handoff without placeholder drift or authority confusion.

## Audit questions

1. Does job state remain SSOT-authoritative in `operations/tasks.json`?
2. Are frame-pointer/state fields stored in `operations/tasks.json` treated as authoritative there rather than being inferred from `QS.json`?
3. Does `QS.json` remain constrained to supplemental execution detail not held in `operations/tasks.json`?
4. Are `JOB.md`, `QF.md`, SessionMemory, and reporting surfaces behaving as derived/projection surfaces rather than peer authorities?
5. Do command handlers resolve the authoritative surfaces independently of the caller's current working directory?
6. Is the observed mismatch a real authority breach, a projection-lag issue that is already documented by contract, or both?

## Clarification: what `frame status` should read

This audit distinguishes between:

- **job state authority**: `operations/tasks.json`
- **supplemental frame-execution detail not present there**: `QS.json`

So `frame status` should not be modeled as “QS replaces task truth after start.” Instead, the strict read path should be:

1. anchor to the canonical workspace root,
2. load the task row from `operations/tasks.json`,
3. read the authoritative state held in `operations/tasks.json`,
4. resolve the registered queststack pointer from the SSOT spine (`spine.root` + `spine.queststack`) only for supplemental operational detail not present in `operations/tasks.json`,
5. read that exact `QS.json` for those operational specifics,
6. fail closed if the registered artifact is missing or unreadable.

Under that stricter model, broad document scans are not the intended primary authority path for frame status. They are, at best, legacy recovery behavior.

## Clarification: what the current registry actually carries

The active `operations/tasks.json` row currently proves strong state authority.

In this planning-session model, that is sufficient. `operations/tasks.json` does **not** need to store frame summaries or other richer operational specifics simply to preserve authority. Those specifics properly belong in `QS.json`.

So the key requirement is not “expand the registry until it mirrors QuestStack detail.” The key requirement is to keep the boundary honest:

- `operations/tasks.json` owns state,
- `QS.json` owns operational specifics,
- and command/read paths must not let `QS.json` override state already held in `operations/tasks.json`.

## Stage-by-stage pipeline map

| Stage                                               | Intended authority                                                                           | Surface(s) reviewed                                                                  | Audit result                                                                                                                                                                                           |
| --------------------------------------------------- | -------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Job registration / lifecycle status                 | `operations/tasks.json`                                                                      | `operations/tasks.json`, report surfaces, lifecycle policy docs                      | Authority is correctly declared and currently populated for the Calamum task.                                                                                                                          |
| Start scaffold / execution artifact materialization | `operations/tasks.json` plus supplemental `QS.json`                                          | `operations/tasks.json`, `QS.json`, `QF.md`, `jobs_utils.py` start/autoscaffold code | Start produced the expected spine artifacts for this lane.                                                                                                                                             |
| Frame status read                                   | `operations/tasks.json` first, then supplemental `QS.json` via SSOT-registered spine pointer | `jobs_utils.py::_handle_job_frame_status`, `_read_qs_json`                           | Intended read layering should be state first and operational detail second, but current implementation mixes pointer resolution with recovery/fallback behavior and is still root-selection-sensitive. |
| Frame advance                                       | `QS.json` with derived `QF.md` regeneration                                                  | `jobs_utils.py::_handle_job_frame_advance`                                           | Contract matches policy: QS first, then full `QF.md` regeneration.                                                                                                                                     |
| Frame pin                                           | `QS.json` with bounded `QF.md` header sync only                                              | `jobs_utils.py::_handle_job_frame_pin`                                               | Contract matches policy: pin writes focus state to `QS.json` and header-syncs `QF.md` only.                                                                                                            |
| SessionMemory stack mirror                          | Derived runtime mirror                                                                       | `jobs_utils.py`, policy docs, known SessionMemory files                              | Correctly described as derived/runtime, not first-order authority.                                                                                                                                     |
| Human-facing frame projection                       | Derived from `QS.json`                                                                       | `QF.md`, policy docs                                                                 | Required projection, but non-authoritative by contract.                                                                                                                                                |

## Evidence: active-lane spine state

### SSOT row state

The active task row in `operations/tasks.json` currently contains:

- `id: calamum-job-0001-tools_gate_lifecycle-20260502`
- `status: in-progress`
- `spine.root: projects/calamum/jobs/JOB_0001_CALAMUM_IMPLEMENTATION_TOOLS-GATE-LIFECYCLE_20260502`
- `spine.queststack: QS.json`
- `spine.questframe_stack_doc: QF.md`

This is the correct repaired-frame-stack shape for the active lane.

### QuestStack state

`QS.json` currently contains:

- `current_focus_frame: qf1`
- a seven-frame stack (`qf1` through `qf7`)
- rich per-frame narrative, evidence routes, governance blocks, and validation declarations

This confirms that the active lane has a materially populated operational execution spine for frame-execution detail. In this planning-session model, that detail supplements and does not replace state already held in `operations/tasks.json`.

### QF projection state

`QF.md` currently presents:

- header metadata showing `Status: in-progress`
- body narrative still saying `Current Focus Frame: (none)` and `Lifecycle posture: open in operations/tasks.json`

This looks inconsistent to a human reader, but current first-order policy explicitly allows `frame pin` to update `QF.md` header metadata only. Under that contract, this body lag is not by itself a classification-grade authority defect.

## Code-path audit findings

### Finding A — confirmed defect: cwd-sensitive frame command root selection

`codesentinel/cli/jobs_utils.py` uses raw cwd-rooting in frame handlers:

- `_handle_job_frame_status(args)` -> `root = Path(getattr(args, 'workspace', None) or Path.cwd())`
- `_handle_job_frame_advance(args)` -> `root = Path(getattr(args, 'workspace', None) or Path.cwd())`
- `_handle_job_frame_pin(args)` -> `root = Path(getattr(args, 'workspace', None) or Path.cwd())`
- `_handle_job_stack_status(args)` -> `root = Path(getattr(args, 'workspace', None) or Path.cwd())`
- `_handle_job_stack_load(args)` -> `root = Path(getattr(args, 'workspace', None) or Path.cwd())`

By contrast, canonical lifecycle and wrapper surfaces elsewhere use the anchored resolver in:

- `codesentinel/utils/workspace_root.py::resolve_workspace_root(...)`
- `codesentinel/cli/job_utils.py::_execute_transition_action(...)`

That resolver is explicitly designed to make workspace-relative artifact lookup stable across nested directories by checking:

1. explicit override,
2. `CODESENTINEL_WORKSPACE`,
3. `CODESENTINEL_REPO_ROOT`,
4. cwd with upward anchoring to `operations/tasks.json`, `.git`, or `pyproject.toml`.

#### Why this matters

The policy contract says execution truth is SSOT-anchored and location-independent. The current `job frame` handlers violate that operationally by letting cwd decide the root used for SSOT lookup and path resolution.

### Finding B — mechanism of failure inside `_read_qs_json(...)`

`jobs_utils._read_qs_json(root, task_id)` is correct only if the supplied `root` is the actual workspace root.

When given a string `task_id`, it tries to enrich that id from SSOT by calling:

- `load_ops_tasks(root)`

If `root` is a nested folder such as `projects/calamum-vulcan`, the function may fail to load the actual `operations/tasks.json` and therefore never enrich the synthetic `{'id': task_id}` dict with the real `spine` block.

Without the enriched `spine`, it cannot apply:

- `_resolve_spine_member_rel(task_dict, 'queststack')`

and therefore never reaches the correctly registered queststack location.

This is not a defect in the task row. It is a defect in how the frame command reaches the task row.

### Finding B.1 — frame-status lookup mixes authoritative pointer resolution with legacy fallback scans

The current helper `jobs_utils._read_qs_json(...)` does more than one thing:

1. attempts the correct SSOT-enriched spine-pointer read,
2. may auto-heal scaffolding when allowed,
3. falls back to `task.path`,
4. falls back again to a glob search under `docs/operations/queststacks`.

That means the present implementation is not a pure single-path authoritative read. The intended authoritative read is the SSOT row plus its registered spine pointer. The extra fallback layers are recovery-oriented behavior that can obscure whether a read succeeded because the registry was correct or because the command wandered into a compatible file by scanning.

This audit classifies that as a **contract gap** even where it does not immediately create wrong output.

### Finding B.2 — the command read path does not yet implement an explicit state-first / QS-second layer

The current frame handlers route directly into `_read_qs_json(...)` for operational readback. That means the implementation still behaves as if QuestStack lookup is the primary frame-state read path, with `operations/tasks.json` acting mainly as the registry that helps find `QS.json`.

Under the planning-session hierarchy captured here, that is incomplete. The intended layered read model is:

1. read authoritative state from `operations/tasks.json`,
2. then read supplemental operational detail from `QS.json`.

That explicit layering is not yet realized in the current handler structure.

### Finding C — the spine member contract itself is healthy

The helper:

- `jobs_utils._resolve_spine_member_rel(task, field_name)`

correctly interprets non-repo-relative spine members like `QS.json` relative to `spine.root`.

Given the active task row:

- `spine.root = projects/calamum/jobs/JOB_0001_CALAMUM_IMPLEMENTATION_TOOLS-GATE-LIFECYCLE_20260502`
- `spine.queststack = QS.json`

it correctly resolves the effective repo-relative queststack path as:

- `projects/calamum/jobs/JOB_0001_CALAMUM_IMPLEMENTATION_TOOLS-GATE-LIFECYCLE_20260502/QS.json`

So the active lane's spine declaration is not the source of drift.

### Finding D — runtime scaffold language still encodes a flatter QS-centric model

The default governance and scaffold strings in `codesentinel/cli/jobs_utils.py` still describe the model too broadly in several places, for example:

- `Keep frame mutation authority in QS.json; do not mutate frame state in QF.md.`
- `QS.json is the authoritative execution spine; subordinate docs are derived.`
- `Mutate frame state in QS.json only; regenerate required derived surfaces in the same transition.`

Those statements are directionally useful for protecting `QF.md` from becoming a peer authority, but they flatten the hierarchy by not distinguishing between:

- task-registry truth in `operations/tasks.json`, and
- supplemental execution detail in `QS.json`.

This is an authority-propagation wording gap inside the implementation scaffold itself.

### Finding E — derived reader projections still overstate `QS.json` in ways that can blur hierarchy

The active `QF.md` for this lane still contains wording such as:

- `Source of truth: .../QS.json`
- `Last authoritative QuestStack focus frame: (none)`
- realignment reminder text that says `QS.json is the authoritative execution spine`

Even when intended as execution-detail shorthand, that wording overstates `QS.json` relative to the planning-session hierarchy captured in this scratchpad. It makes the reader surface sound as though `QS.json` is the sole authority for frame state rather than a supplemental execution artifact beneath the task registry.

This is a derived-surface wording gap. It does not create authority by itself, but it can mislead planning and operator interpretation.

### Finding E.1 — the QF generator/template derives from the right sources but describes them too loosely

The active QF generator and template do **not** appear to pull truth from an undefined source. Their actual derivation path is still bounded to the declared authority stack:

- state header fields such as lifecycle posture come from `operations/tasks.json`,
- operational frame detail comes from `QS.json`,
- the output is rendered as a derived human-facing projection.

So the problem here is primarily wording, not hidden authority theft. The generator/template phrases such as `Source of truth: <job_root>/QS.json` are too broad for the clarified model, but they do not by themselves indicate that the artifact is reading from an undefined source outside the stack.

### Finding E.2 — active-lane derived/runtime artifacts stay inside the declared stack

In the active lane, the reviewed artifacts still derive from bounded sources that are identifiable and classifiable:

- `JOB.md` is a paired/derived reader for `JOB.json` plus sanctioned lifecycle header sync.
- `QF.md` is a derived reader projection from `QS.json` with sanctioned header sync from `operations/tasks.json`.
- `.agent_session/task_stack.json` and `.agent_session/queststack_journal.jsonl` are runtime mirrors/evidence surfaces when populated from the canonical job/frame commands; they are not first-order authority for this lane.
- `logs/behavioral/jobs/*.jsonl` are event evidence only.

This means the active-lane problem is not rogue derivation from unknown files. The active-lane problem is that the hierarchy is communicated and enforced imperfectly.

### Finding E.3 — adjacent historical SessionMemory QuestStack SSOT surfaces describe a different model and must stay demoted for this lane

The broader codebase still contains older SessionMemory-centered QuestStack planning surfaces, for example:

- `docs/operations/plans/QUESTSTACK_SSOT_REMEDIATION_PLAN_20260101.md`
- `docs/operations/SESSION_MEMORY_SURFACE_ARTIFACT_INVENTORY_20251215.md`

Those surfaces describe `.agent_session/task_stack.json` and `.agent_session/queststack_journal.jsonl` as SSOT for a SessionMemory QuestStack model.

That is a materially different authority model from the current job/frame hierarchy under review here. For this Calamum lane, those surfaces must remain classified as:

- historical,
- adjacent architecture context, or
- separate subsystem documentation,

but **not** active authority for job state or operational frame specifics.

This is an adjacent-classification gap rather than an active-lane derivation defect, but it is important because an uninformed reader could otherwise import the wrong SSOT model into this planning conversation.

### Finding E.4 — legacy authority claims audit: preserve historical truth, but label it superseded for this lane

This audit does **not** recommend overwriting older authority claims when they accurately preserve the model that existed at the time they were written. Historical truth should remain legible. The requirement is classification, not erasure.

The legacy-authority problem in this codebase is therefore:

- older surfaces may accurately record an earlier or separate subsystem authority model,
- but they can still mislead current planning if they are not clearly labeled as superseded, historical, or non-authoritative for the active lane.

Examples identified in this investigation:

1. **Historical SessionMemory QuestStack SSOT model**
   - Surfaces such as `docs/operations/plans/QUESTSTACK_SSOT_REMEDIATION_PLAN_20260101.md` and `docs/operations/SESSION_MEMORY_SURFACE_ARTIFACT_INVENTORY_20251215.md` describe `.agent_session/task_stack.json` and `.agent_session/queststack_journal.jsonl` as SSOT within a SessionMemory QuestStack design.
   - That may be historically accurate for that subsystem discussion.
   - For this Calamum job/frame lane, however, those claims are **superseded / non-authoritative** and must not be imported as active execution authority.

2. **Broad QS-centric wording in runtime scaffolds and templates**
   - Phrases such as `QS.json is the authoritative execution spine` and `Source of truth: <job_root>/QS.json` preserve the historical implementation shorthand used by current generators/templates.
   - These phrases should be preserved as evidence of how the system was previously described.
   - For the clarified hierarchy in this planning lane, they are **too broad and therefore superseded as present-tense authority wording**, even though they remain useful historical implementation evidence.

3. **Older repo paperwork and QuestStack view surfaces**
   - Legacy repo QuestStack paperwork under `docs/operations/queststacks/` and related logs may preserve prior execution/read-model assumptions.
   - Those assumptions should be treated as historical/generated views unless the current first-order authority explicitly elevates them.

Recommended classification rule for this lane:

- preserve the legacy claim,
- keep the original file intact,
- but label it in planning/audit language as one of:
  - `historical truth`,
  - `superseded for current lane authority`,
  - `non-authoritative for current execution decisions`, or
  - `adjacent subsystem model; not this lane's SSOT`.

That preserves repo memory without allowing historical wording to silently govern current execution reasoning.

### Finding F — `frame pin` projection behavior matches current policy

Current first-order SSOT and policy docs explicitly state:

- `codesentinel job frame pin` updates `QS.json` focus state
- it may sync `QF.md` header metadata only
- full `QF.md` regeneration is reserved for start/scaffold, frame advance, and close-projection normalization paths

The implementation matches that contract:

- `_handle_job_frame_pin(...)` writes `current_focus_frame` to `QS.json`
- then calls `_sync_qf_projection_header_from_task(...)`
- it does not call `_regenerate_qf_projection_from_qs(...)`

Therefore, body-level lag inside `QF.md` after pin is consistent with design as currently documented.

## Live reproduction evidence

The same command was run twice with the same `task_id` and same on-disk artifacts:

1. From repo root:
   - `codesentinel job frame pin calamum-job-0001-tools_gate_lifecycle-20260502 --frame-id qf1`
   - Result: success
2. From nested folder `projects/calamum-vulcan`:
   - `codesentinel job frame pin calamum-job-0001-tools_gate_lifecycle-20260502 --frame-id qf1`
   - Result: `No QuestStack JSON found for task 'calamum-job-0001-tools_gate_lifecycle-20260502'.`

Because the task row, queststack file, and task id were unchanged, the variable that changed was the working directory. That is conclusive evidence that the frame-pin lookup path is improperly location-sensitive.

## Audit classification

### Confirmed authority-preserving behavior

- Job state authority is correctly declared in `operations/tasks.json`.
- The active task row correctly registers the supplemental QuestStack spine used to reach `QS.json`.
- `QF.md` is correctly classified by policy as a required non-authoritative projection.
- `frame pin` being header-only is documented by first-order authority and implemented accordingly.

### Confirmed defect

- `job frame` command-family handlers are using raw cwd-rooting instead of canonical workspace-root resolution.
- This makes frame-state lookup operationally depend on caller location, which breaks the intended SSOT contract even though the authoritative row and queststack are valid.

### Additional gaps surfaced in this broader investigation

- **Read-layer gap:** frame handlers do not yet implement an explicit state-first / QS-second read contract.
- **Scaffold wording gap:** `jobs_utils.py` default governance strings still flatten the hierarchy into a QS-centric posture.
- **Derived-reader wording gap:** active `QF.md` wording still overstates `QS.json` as sole truth in places where hierarchical layering should be made explicit.
- **Adjacent historical-model gap:** older SessionMemory QuestStack planning surfaces still describe a different SSOT model and must remain demoted/out-of-authority for this lane.
- **First-order wording gap (not edited in this planning pass):** the current policy/SSOT prose still speaks more broadly about `QS.json` than this planning-session clarification allows.

### Not classified as a defect in this audit

- `QF.md` body narrative lag after `frame pin`
- SessionMemory mirror state not being first-order authority
- existence of supporting/historical surfaces that are already demoted by policy

## Conceptual system map

### Authority layers

1. **Pipeline registry authority**
   - `operations/tasks.json`
   - owns lifecycle status, task identity, routing, spine registration, and state truth

2. **Supplemental execution artifact after start**
   - `QS.json`
   - carries frame-execution detail, narrative, and other operational data not held in `operations/tasks.json`
   - must not override state truth already held in `operations/tasks.json`

3. **Required human-facing projection**
   - `QF.md`
   - derived from `QS.json`, not peer authority

4. **Runtime mirrors / telemetry**
   - SessionMemory stack
   - queststack journal
   - behavioral logs
   - evidence only; not lifecycle authority

### Affected system goals

The active Calamum lane depends on a truthful frame pipeline because its planning program is intentionally multi-stage and governance-heavy. If frame commands can only find the queststack from some directories but not others, the operator-facing execution system gives false signals about pipeline readiness and obscures whether failures are due to real missing artifacts or a broken lookup surface.

## Audit conclusions

1. The repository's declared authority model is internally coherent.
2. The active Calamum task row and queststack artifact are present and materially correct.
3. `frame status` should read authoritative state from `operations/tasks.json` first, and only then read supplemental execution detail from `QS.json` through the SSOT-registered pointer chain.
5. The pipeline does not currently honor the intended location-independence of SSOT-backed frame operations.
6. The implementation scaffold and derived projections still propagate a flatter QS-centric wording model than this hierarchy allows.
7. The most important remediation targets are: state-first read layering, frame-handler root-resolution, and demotion of broad fallback scan behavior in `_read_qs_json(...)`.
8. `QF.md`'s stale body after pin should not be used as evidence of multi-authority drift, because current policy explicitly permits that bounded-sync behavior.
9. In the active lane, reviewed artifacts do not appear to derive truth from undefined sources outside the declared stack; the remaining problem is misclassification/miscommunication of bounded sources, plus adjacent historical surfaces that describe a different model and must stay demoted.

## Phased alignment plan (not executed in this audit)

### Phase 0 — authority freeze and classification discipline

Goal:

- freeze the clarified authority model for this lane in planning language before code or first-order doc edits begin.

Required outcomes:

- preserve `operations/tasks.json` as the state authority;
- preserve `QS.json` as the operational-specifics authority;
- preserve `QF.md`, SessionMemory mirrors, and logs as derived/evidence surfaces only;
- classify older conflicting or broader claims as historical/superseded rather than silently letting them govern the lane.

Why first:

## QF1 execution record — 2026-05-02T18:10:40Z

- qf1 was executed against the declared planning corpus rather than against derived-reader shorthand alone.
- Corpus readback covered:
   - `CALAMUM_MONITOR_EVIDENCE_ARCHITECTURE_PROPOSAL_20260501.md`
   - `CALAMUM_MONITOR_EVIDENCE_ARCHITECTURE_SCRATCHPAD_20260501.md`
   - `CALAMUM_TEST_CHILD_REPO_IMPLEMENTATION_PLAN_20260423.md`
   - `CALAMUM_TEST_V2_TARGETS_20260423.md`
   - `projects/calamum/.calamum/project.json`
   - `projects/calamum/pyproject.toml`
- Frozen qf1 findings:
   - Accepted top-level operator grammar remains `calamum test`, `calamum monitor`, and `calamum project`.
   - Project-scoped retained-evidence routing remains `calamum project evidence`.
   - Backend tool names (PyShark, TShark, dumpcap, USBPcap, Heimdall, Windows PnP) remain adapter/readiness metadata only, not primary operator nouns.
   - `calamum-test` remains distribution/package metadata; standalone runtime/CLI identity remains `calamum`.
   - The v2 note remains exploratory except for the previously approved silent Polymath integration direction.
- Execution note:
   - The live stack was in a hybrid pinned-open posture (`current_focus_frame = qf1` while `qf1.status = open`), so qf1 findings were materialized directly into `QS.json` before using the native advance path. This avoids the known skip-to-qf2 hazard documented earlier for a blind `codesentinel job frame advance` from that posture.

## QF2 execution record — 2026-05-02T18:14:49Z

- qf2 was executed against the live implementation seams declared in the QuestStack evidence routes.
- Files read for the substrate/compatibility map:
   - `projects/calamum/src/calamum/cli.py`
   - `projects/calamum/src/calamum/api.py`
   - `projects/calamum/src/calamum/projects.py`
   - `projects/calamum/src/calamum/runner.py`
   - `projects/calamum/src/calamum/reports.py`
   - `projects/calamum/src/calamum/signing.py`
   - `projects/calamum/src/calamum/catalog.py`
   - `projects/calamum/src/calamum/layout.py`
   - `projects/calamum/src/calamum/render.py`
   - `projects/calamum/tests/test_cli.py`
- Frozen qf2 findings:
   - Only `calamum test` is currently top-level; `project`, `runs`, and `reports` are nested under `test` in `cli.py`.
   - `projects.py` already owns the reusable project-context layer: descriptor registration, alias resolution, active-project state, overlays, and retained root derivation.
   - `runner.py` and `reports.py` already implement the retained-evidence core for runs, manifests, checksums, aggregate reports, receipts, and history.
   - `signing.py`, `catalog.py`, `layout.py`, and `render.py` already provide reusable signing/schema/output primitives that can survive route migration.
   - `api.py` is already a thin facade over the retained-evidence/project substrate.
   - `tests/test_cli.py` currently locks grouped help plus `calamum test project ...`, `calamum test runs ...`, and `calamum test reports ...` behavior, so future canonical expansion must preserve or alias those surfaces deliberately.
- Execution note:
   - The native frame-advance path successfully moved the stack from qf1 to qf2. SessionMemory stack-replace refresh remains guarded/not authorized through the current native `job stack load --replace --force` lane, so runtime-mirror duplication remains a known observational artifact rather than the execution authority for this job.

- this phase prevents later remediation from solving the wrong problem or broadening `tasks.json` beyond the intended state-only role.

### Phase 1 — runtime path hardening

Goal:

- remove location-sensitive and fallback-heavy behavior from the active job/frame command path.

Required outcomes:

- replace raw cwd root selection in `jobs_utils` frame/stack handlers with canonical workspace-root resolution;
- narrow `frame status` / `frame pin` / `frame advance` QuestStack resolution to the SSOT row plus registered spine pointer as the primary read path;
- demote glob/document-scan fallback to explicit recovery mode rather than ordinary read behavior.

Why this matters:

- the active reproduced failure is a runtime path defect, not a planning abstraction issue.

### Phase 2 — state-first / operational-detail-second read model

Goal:

- make handler behavior explicitly reflect the clarified hierarchy.

Required outcomes:

- frame/status handlers read state from `operations/tasks.json` first;
- those handlers read `QS.json` second for supplemental operational specifics only;
- no handler treats `QS.json` as allowed to override state already held in `operations/tasks.json`.

Why this matters:

- today the implementation still behaves too much like a QuestStack-first read path with SSOT used mainly as a locator.

### Phase 3 — wording and projection cleanup

Goal:

- align generator, template, and reader wording with the clarified model without erasing historical evidence.

Required outcomes:

- update scaffold/governance wording in runtime generators and derived-reader templates so they no longer flatten the hierarchy into broad `QS.json` authority claims;
- preserve legacy claims as historical truth, but label them superseded/non-authoritative for this lane where appropriate;
- ensure derived readers clearly indicate their bounded derivation path rather than implying they are peer authorities.

Why this matters:

- the remaining active-lane confusion is now mostly a classification and communication problem.

### Phase 4 — first-order authority reconciliation

Goal:

- reconcile the planning clarification with first-order present-tense authority prose in a separately authorized pass.

Required outcomes:

- align `docs/operations/ssot/JOBS_AND_EXECUTION_SSOT.md` with the clarified hierarchy;
- align `PP_OPS_PROTOCOL_POL_JOB_PIPELINE_AUTHORITY_AND_EXECUTION_ARTIFACTS_20260312.md` and its JSON sidecar with the same model;
- keep older subsystem or historical models preserved, but clearly demoted where they are no longer current authority for this lane.

Why this is later:

- this phase touches first-order authority and was explicitly out of scope for the current scratchpad-only planning pass.

### Phase 5 — validation and closure-grade confirmation

Goal:

- prove the clarified model is actually enforced in code and communicated honestly across the repo surfaces that matter for this lane.

Required outcomes:

- re-run frame status/pin from repo root and nested directories after repair to validate location-independence;
- confirm derived readers still render correctly while staying non-authoritative;
- confirm SessionMemory and behavioral logs remain evidence/mirror surfaces rather than active state authorities;
- decide whether the current `QF.md` header-only pin contract remains desirable for operator ergonomics, treating that as a policy/product decision rather than a hidden bug.

## Plan validation against live repo state

This phased plan is considered complete for the current planning pass because it maps directly to the live repo conditions that were actually verified:

### Checked live and covered by the plan

- **Active registry state exists and is healthy**
   - verified in `operations/tasks.json`
   - covered by Phases 1, 2, and 5

- **Active QuestStack spine exists and is materially populated**
   - verified in the active `QS.json`
   - covered by Phases 1, 2, 3, and 5

- **Derived `QF.md` exists and currently overstates QS authority in wording**
   - verified in the active `QF.md`
   - covered by Phases 3 and 5

- **Runtime handler defect is real and reproducible**
   - verified by root-vs-nested `frame pin` reproduction
   - covered by Phases 1 and 5

- **Read-layer contract is still too implicit and too QS-centric**
   - verified in `codesentinel/cli/jobs_utils.py`
   - covered by Phases 2 and 5

- **Generator/template wording still flattens hierarchy**
   - verified in `jobs_utils.py` and `QF_JOB_START.md.template`
   - covered by Phase 3

- **Adjacent historical SessionMemory QuestStack model still exists in repo docs**
   - verified in SessionMemory inventory/remediation docs
   - covered by Phases 0, 3, and 4

- **Affected-system planning corpus has been ingested broadly enough for this lane**
   - active job packet, active QS/QF, Calamum proposal/scratchpad, Calamum planning docs, project descriptor, package metadata, implementation code, first-order SSOT/policy docs, and adjacent SessionMemory QuestStack docs were all reviewed in this planning exercise
   - covered across all phases

### Coverage assessment

This plan covers all bases needed to align the repo with the clarified authority model for this lane:

1. **authority definition** — Phase 0
2. **runtime lookup correctness** — Phase 1
3. **hierarchical read semantics** — Phase 2
4. **projection/template wording honesty** — Phase 3
5. **first-order authority reconciliation** — Phase 4
6. **post-repair proof and regression checks** — Phase 5

### Explicit non-gaps / exclusions

This plan intentionally does **not** require:

- expanding `operations/tasks.json` to store frame summaries or richer operational specifics;
- overwriting historical documents that preserve older but real authority claims;
- reclassifying `QF.md` as authoritative;
- treating SessionMemory mirrors or behavioral logs as state authority for this lane.

That exclusion set is important because it prevents the remediation plan from drifting away from the clarified model it is supposed to enforce.

## Execution checklist for the planned update

Use this checklist to drive execution of the repo-alignment work once implementation is authorized. The checklist is intentionally front-loaded with preparation and corpus-ingest tasks so the remediation does not run ahead of the planning understanding.

### A. Preparation and authority freeze

- [x] Re-state the active-lane authority model at kickoff: `operations/tasks.json` owns state; `QS.json` owns supplemental operational specifics; `QF.md`, SessionMemory mirrors, and logs are derived/evidence surfaces.
- [x] Confirm the active task id, job root, and spine registration for `calamum-job-0001-tools_gate_lifecycle-20260502` from `operations/tasks.json` before touching runtime logic.
- [x] Record that this scratchpad is planning/support only and that first-order authority still lives in `operations/tasks.json`, `JOBS_AND_EXECUTION_SSOT.md`, and `PP_OPS_PROTOCOL_POL_JOB_PIPELINE_AUTHORITY_AND_EXECUTION_ARTIFACTS_20260312.md`.
- [x] Freeze the non-goals for the update: no expansion of `operations/tasks.json` into a QuestStack mirror, no promotion of `QF.md` to authority, no erasure of historically accurate legacy docs.

### B. Corpus ingest and affected-system mapping

- [x] Re-read the first-order governance corpus:
   - [x] `operations/tasks.json`
   - [x] `docs/operations/ssot/JOBS_AND_EXECUTION_SSOT.md`
   - [x] `docs/policies/operations/OPERATIONS_POLICY/PP_OPS_PROTOCOL_POL_JOB_PIPELINE_AUTHORITY_AND_EXECUTION_ARTIFACTS_20260312.md`
   - [x] `.github/instructions/execution-authority.instructions.md`
- [x] Re-read the active-lane execution corpus:
   - [x] `JOB.json`
   - [x] `JOB.md`
   - [x] `QS.json`
   - [x] `QF.md`
   - [x] `CALAMUM_MONITOR_EVIDENCE_ARCHITECTURE_PROPOSAL_20260501.md`
   - [x] `CALAMUM_MONITOR_EVIDENCE_ARCHITECTURE_SCRATCHPAD_20260501.md`
- [x] Re-read the broader Calamum planning corpus:
   - [x] `projects/calamum/planning/CALAMUM_TEST_CHILD_REPO_IMPLEMENTATION_PLAN_20260423.md`
   - [x] `projects/calamum/planning/CALAMUM_TEST_V2_TARGETS_20260423.md`
   - [x] `projects/calamum/.calamum/project.json`
   - [x] `projects/calamum/pyproject.toml`
- [x] Re-read the affected implementation surfaces:
   - [x] `codesentinel/cli/job_utils.py`
   - [x] `codesentinel/cli/jobs_utils.py`
   - [x] `codesentinel/utils/workspace_root.py`
   - [x] `codesentinel/utils/ops_tasks_registry.py`
   - [x] `codesentinel/assets/VAULT_templates/jobpipeline/QF_JOB_START.md.template`
- [x] Re-read adjacent historical/parallel-model surfaces so they can be preserved but demoted correctly:
   - [x] `docs/operations/plans/QUESTSTACK_SSOT_REMEDIATION_PLAN_20260101.md`
   - [x] `docs/operations/SESSION_MEMORY_SURFACE_ARTIFACT_INVENTORY_20251215.md`
   - [x] No additional touched `docs/operations/queststacks/` reader surfaces were required for this execution pass.
- [x] Update the affected-system map if new dependencies or reader surfaces are discovered during the re-read.

### C. Runtime-path defect confirmation

- [x] Reproduce the root-vs-nested-directory behavior for `codesentinel job frame pin` and `codesentinel job frame status` before remediation.
- [x] Confirm whether the failure enters through raw cwd root selection, fallback scanning, or both.
- [x] Trace the live read path from frame handler entrypoint to task-row load, spine resolution, `QS.json` load, and `QF.md` sync.
- [x] Record the exact functions that need intervention without widening scope beyond the affected path.

### D. State-first / operational-detail-second design check

- [x] Write down the intended handler contract before editing code:
   - [x] state comes from `operations/tasks.json` first;
   - [x] operational specifics come from `QS.json` second;
   - [x] `QS.json` must not override state already held in `operations/tasks.json`.
- [x] Identify which fields are state-owned versus operational-detail-owned in the active lane.
- [x] Verify that the proposed handler changes preserve the current start/advance/pin product behavior unless a separate policy decision explicitly changes it.
- [x] Confirm that fallback scans, if kept at all, are recovery-only and not ordinary authority reads.

### E. Wording and reader-surface alignment prep

- [x] Inventory runtime strings, templates, and reader text that currently flatten the hierarchy into a QS-centric claim.
- [x] Classify each touched wording surface as one of:
   - [x] first-order authority
   - [x] derived reader
   - [x] runtime scaffold
   - [x] historical/supporting context
- [x] For each legacy wording surface, decide whether the correct action is:
   - [x] preserve unchanged as historical truth,
   - [x] preserve but add superseded/non-authoritative labeling,
   - [x] or update present-tense wording in a currently authoritative/derived surface.

### F. Implementation execution checklist

- [x] Replace raw cwd-root selection in the affected frame/stack handlers with canonical workspace-root resolution.
- [x] Make the frame/status read path explicitly load `operations/tasks.json` first and `QS.json` second.
- [x] Keep the SSOT row plus registered spine pointer as the normal resolution path for `QS.json`.
- [x] Demote broad scan fallback to explicit recovery behavior rather than standard lookup.
- [x] Preserve existing sanctioned `frame pin` behavior unless a separately approved policy/product decision changes it.
- [x] Limit edits to the minimum set of files required to realize the corrected authority model.

### G. Validation checklist

- [x] Re-run `frame pin` from repo root and at least one nested folder after remediation.
- [x] Re-run `frame status` from repo root and at least one nested folder after remediation.
- [x] Confirm that the same authoritative task row and registered `QS.json` are reached regardless of cwd.
- [x] Confirm that derived surfaces still render correctly and remain non-authoritative.
- [x] Confirm that no new path allows `QS.json` to override state already held in `operations/tasks.json`.
- [x] Confirm that SessionMemory and logs still behave as mirrors/evidence only.

### H. Completion / alignment review

- [x] Check the finished change set against the phased plan in this scratchpad and confirm every phase touched by the implementation has corresponding evidence.
- [x] Check the finished change set against the live repo state again to ensure no affected surface was missed.
- [x] Verify that the repo now communicates the clarified model honestly across state, runtime read paths, derived readers, and preserved historical surfaces.
- [x] Verify that no part of the remediation accidentally widened authority, rewrote planning scope, or erased historical truth.
- [x] Produce a final audit note identifying what was aligned, what remains future-authorized work, and any residual policy/product decisions still open.

## Execution follow-on note — 2026-05-02

The planning/remediation update described in this scratchpad has now been executed in the repo. The planning findings above remain preserved as historical planning context; the note below records the later implementation follow-on without rewriting that history.

### Implemented surfaces

- `codesentinel/cli/jobs_utils.py`
   - frame and stack handlers now resolve the canonical workspace root rather than using raw cwd selection;
   - frame commands now load the authoritative task row from `operations/tasks.json` first before resolving `QS.json`;
   - ordinary frame reads now keep broad QuestStack fallback behavior behind explicit recovery/autoheal posture instead of treating it as the normal path;
   - runtime governance wording now distinguishes `operations/tasks.json` state authority from `QS.json` supplemental execution detail.
- `codesentinel/assets/VAULT_templates/jobpipeline/QF_JOB_START.md.template`
   - QF template wording now describes `QS.json` as the supplemental execution-detail source and `operations/tasks.json` as the state authority.
- `docs/operations/ssot/JOBS_AND_EXECUTION_SSOT.md`
   - present-tense SSOT wording now preserves `operations/tasks.json` as state authority after start while classifying `QS.json` as the supplemental execution artifact for detail not stored there.
- `docs/policies/operations/OPERATIONS_POLICY/PP_OPS_PROTOCOL_POL_JOB_PIPELINE_AUTHORITY_AND_EXECUTION_ARTIFACTS_20260312.md`
- `docs/policies/operations/OPERATIONS_POLICY/pp/PP_OPS_PROTOCOL_POL_JOB_PIPELINE_AUTHORITY_AND_EXECUTION_ARTIFACTS_20260312.json`
   - first-order policy prose and machine-readable policy summary now match the clarified hierarchy.

### Validation executed

- Direct native runtime validation through `codesentinel job frame pin`:
   - repo root: pass
   - nested `projects/calamum-vulcan`: pass
- Direct native runtime validation through `codesentinel job frame status --json`:
   - repo root: pass
   - nested `projects/calamum-vulcan`: pass
   - output now reports `task_status`, `status_authority`, and the SSOT-resolved QuestStack path.
- Required native validation through `calamum test`:
   - `calamum test run seed-cli-smoke --job authority-model-root-fix-20260502`
   - result: pass
   - retained run id: `20260502T174418Z-seed-cli-smoke`

### Deliberate non-mutation

- Existing derived `QF.md` artifacts were **not** hand-edited as part of this remediation.
- The wording improvements for QF projections were applied to runtime generation/template surfaces so future canonical regeneration paths render the corrected authority language.
- This preserves the command-owned mutation boundary for derived lifecycle artifacts.

## QF projection regeneration investigation addendum — 2026-05-02

This addendum preserves the later investigation requested during active frame-stack execution after the lane had already advanced to `qf3` in the authoritative execution surfaces but the required derived `QF.md` projection still appeared stale to the operator.

This section remains:

- investigative / planning / support only;
- non-authoritative for lifecycle state;
- subordinate to `operations/tasks.json`, `docs/operations/ssot/JOBS_AND_EXECUTION_SSOT.md`, and `docs/policies/operations/OPERATIONS_POLICY/PP_OPS_PROTOCOL_POL_JOB_PIPELINE_AUTHORITY_AND_EXECUTION_ARTIFACTS_20260312.md`.

### Why this addendum exists

The earlier audit sections above already captured:

- the state-authority hierarchy,
- the root-selection defect in frame handlers,
- the required state-first / supplemental-detail-second read model, and
- the broader QS-centric wording cleanup plan.

What they did **not** yet preserve in one place was the later, narrower investigation into a different defect class:

- the live frame stack had already advanced from `qf2` to `qf3`,
- `operations/tasks.json` and `QS.json` agreed on that fact,
- but the persisted `QF.md` body still displayed the older pre-advance state.

The operator explicitly requested a concrete, no-guessing investigation of whether the `frame advance` path was actually triggering required QF regeneration, plus a preserved resolution plan.

### Additional corpus ingested for this investigation pass

The narrower QF-regeneration investigation was grounded in the already-ingested job corpus **plus** a fresh readback of the following affected-system surfaces relevant to the active `qf3` lane and the broader Calamum project goals:

#### Active-lane execution surfaces

- `projects/calamum/jobs/JOB_0001_CALAMUM_IMPLEMENTATION_TOOLS-GATE-LIFECYCLE_20260502/JOB.json`
- `projects/calamum/jobs/JOB_0001_CALAMUM_IMPLEMENTATION_TOOLS-GATE-LIFECYCLE_20260502/JOB.md`
- `projects/calamum/jobs/JOB_0001_CALAMUM_IMPLEMENTATION_TOOLS-GATE-LIFECYCLE_20260502/QS.json`
- `projects/calamum/jobs/JOB_0001_CALAMUM_IMPLEMENTATION_TOOLS-GATE-LIFECYCLE_20260502/QF.md`
- this scratchpad itself

#### Calamum planning and product-goal corpus

- `projects/calamum/jobs/JOB_0001_CALAMUM_IMPLEMENTATION_TOOLS-GATE-LIFECYCLE_20260502/CALAMUM_MONITOR_EVIDENCE_ARCHITECTURE_PROPOSAL_20260501.md`
- `projects/calamum/jobs/JOB_0001_CALAMUM_IMPLEMENTATION_TOOLS-GATE-LIFECYCLE_20260502/CALAMUM_MONITOR_EVIDENCE_ARCHITECTURE_SCRATCHPAD_20260501.md`
- `projects/calamum/planning/CALAMUM_TEST_CHILD_REPO_IMPLEMENTATION_PLAN_20260423.md`
- `projects/calamum/planning/CALAMUM_TEST_V2_TARGETS_20260423.md`
- `projects/calamum/README.md`
- `projects/calamum/SECURITY.md`

#### Runtime implementation surface used by the active lane

- `codesentinel/cli/jobs_utils.py`

This broader ingest matters because the `QF.md` defect is not an isolated markdown annoyance. In this lane, `QF.md` is the required human-facing projection for a seven-frame planning program whose purpose is to produce a safe execution-ready handoff for:

- top-level `calamum test`, `calamum monitor`, and `calamum project` command-family planning;
- project-scoped evidence retention and review under project context;
- readiness / no-go packet design;
- and a future downstream Vulcan consumer boundary that depends on accurate, legible planning-state projection.

If the required `QF.md` projection drifts silently while the authoritative machine-readable spine advances correctly, the operator loses the intended human-readable frame-stack narrative needed for safe planning execution.

### Immediate execution context when the investigation began

At the moment this narrower investigation began, the authoritative execution surfaces already showed:

- task id: `calamum-job-0001-tools_gate_lifecycle-20260502`
- task status in `operations/tasks.json`: `in-progress`
- current focus frame in `QS.json`: `qf3`
- qf1: `completed`
- qf2: `completed`
- qf3: `in-progress`

But the persisted `QF.md` body still showed the older seed-style posture, including stale body text equivalent to:

- current focus frame: `(none)` or otherwise non-current;
- no admitted active frame in the narrative body;
- frame table/body content not reflecting the `qf2 -> qf3` advance.

That mismatch is important to classify correctly:

- it is **not** evidence that `operations/tasks.json` lost authority;
- it is **not** evidence that `QS.json` failed to record the frame advance;
- it **is** evidence that the required derived projection became stale relative to already-correct authority surfaces.

### Narrowed investigation scope requested by the operator

The operator explicitly narrowed the investigation after an earlier side-path discussion of `frame pin` behavior and required that the active investigation answer only this question:

- within the **current frame-advance execution path**, is required `QF.md` regeneration actually firing or not?

For this addendum, that instruction is preserved as a scope rule:

- `frame pin` behavior is relevant historical context for overall projection semantics,
- but it is **not** the causal scope of the active defect being investigated here,
- because the stale `QF.md` was observed immediately after active frame-stack advancement, not as a pin-only artifact.

### Concrete findings from direct examination

#### Finding 1 — authoritative state was healthy before the projection check

Direct comparison across the active-lane artifacts established:

- `operations/tasks.json` still carried the task as `in-progress`;
- `QS.json` still carried `current_focus_frame: qf3` with qf1/qf2 completed and qf3 in-progress;
- the native frame-status surface agreed with that current machine-readable state.

Therefore the problem domain was already narrowed to the required derived projection, not the underlying lifecycle state.

#### Finding 2 — `frame advance` does reach the regenerator callsite

Direct code read of `codesentinel/cli/jobs_utils.py` showed that `_handle_job_frame_advance(...)` does not merely mutate `QS.json` and stop. The active path explicitly performs:

1. authoritative task/QS read and frame mutation work,
2. `_write_qs_json(qs_path, qs_data)`, then
3. `_regenerate_qf_projection_from_qs(root, task_id, qs_path, qs_data)`.

That means the specific claim "the advance path never calls the regenerator" is **refuted** by direct code examination.

#### Finding 3 — the renderer itself can produce the correct qf3 projection from live inputs

To eliminate speculation about whether the renderer/template path itself was incapable of expressing the current state, the same renderer used by the regenerator was invoked directly against the live authoritative inputs:

- live task row from `operations/tasks.json`
- live `QS.json`
- `_render_qf_stack_doc(...)`

That direct render succeeded and produced output showing the correct modern state, including:

- `Current Focus Frame: qf3`
- qf1 completed
- qf2 completed
- qf3 in-progress

So the defect is **not** that the current `QS.json` shape is unrenderable or that the renderer template fundamentally cannot project the live lane state.

#### Finding 4 — the concrete defect domain is the regeneration persistence / verification lane

Given Findings 1 through 3, the remaining supported conclusion is:

- the advance handler reaches the regenerator callsite;
- the renderer can generate the correct projection from current authority inputs;
- yet the persisted `QF.md` remained stale.

Therefore the defect lies in the lane between:

- regenerator invocation,
- render/write execution,
- and verification that the persisted `QF.md` actually reflects the just-written authoritative `QS.json` state.

In other words: the stale `QF.md` is a **projection persistence/verification defect**, not an authority-state defect.

#### Finding 5 — the current regenerator contract is too weak for a required projection

Direct code read of `_regenerate_qf_projection_from_qs(...)` showed that it is currently implemented as a best-effort helper that returns silently on failure paths.

That means:

- the lifecycle mutation can succeed,
- the command can continue reporting successful advancement,
- while the required human-facing `QF.md` projection is left stale,
- and without a hard signal that the regeneration stage failed.

For a required projection in an active planning lane, that is a contract weakness even when the underlying machine-readable state remains correct.

### Affected-system mapping for this specific defect

This narrower defect sits at the intersection of several systems already mapped elsewhere in this scratchpad:

1. **Job/lifecycle authority system**
   - keeps task state in `operations/tasks.json`
   - healthy in this incident

2. **QuestStack operational-detail system**
   - keeps frame execution detail in `QS.json`
   - healthy in this incident

3. **Required human-facing frame-stack projection system**
   - persists `QF.md` as the required operator-readable projection
   - stale in this incident

4. **Frame-advance orchestration path in `jobs_utils.py`**
   - correctly reaches the regeneration callsite
   - lacks a strict verified-success contract for the required derived write

5. **Planning-execution usability for the Calamum lane**
   - depends on faithful human-readable frame projection because this is a multi-frame planning and handoff job, not merely a machine-state ledger

### Classification of the defect

This investigation classifies the issue as:

- **real defect**: yes
- **authority breach**: not in the sense of incorrect state authority ownership
- **derived-projection failure**: yes
- **active-lane operator-risk issue**: yes, because the required human-facing projection can silently misstate current frame posture during planning execution

This is materially different from the earlier documented `frame pin` bounded-header-sync behavior. That bounded pin behavior may still be policy-consistent. The defect here is that a full `frame advance` transition, which should regenerate the required projection, can leave the persisted projection stale without failing closed.

## Resolution plan for the QF regeneration defect (planning only; not executed here)

The resolution plan below preserves the operator-requested fix direction without claiming implementation in this addendum.

### Phase A — freeze the intended contract in lane language

Goal:

- explicitly record that `QF.md` regeneration during `frame advance` is a **required verified stage**, not a best-effort courtesy side effect.

Required outcome:

- a successful frame advance must mean both:
  - authoritative frame mutation succeeded in `QS.json`, and
  - the required `QF.md` projection now reflects that same state.

Why first:

- without freezing the contract, later implementation may patch symptoms while preserving silent projection drift.

### Phase B — harden `_regenerate_qf_projection_from_qs(...)` from best-effort to fail-closed behavior

Goal:

- remove silent-success behavior for required projection regeneration in the `frame advance` lane.

Required outcomes:

- distinguish and surface failures for:
  - task-row reload failure,
  - QuestStack path normalization failure,
  - QF path resolution failure,
  - render failure,
  - file write failure.
- do not let `frame advance` print or return success if the required projection stage failed.

Why this matters:

- `QF.md` is not optional decoration in this lane; it is the required human-facing projection of active frame execution.

### Phase C — add post-write verification

Goal:

- verify that the persisted `QF.md` matches the just-mutated state rather than merely assuming the write succeeded.

Required outcomes:

- after writing `QF.md`, re-read or otherwise verify the persisted file;
- confirm that the persisted projection reflects at least the newly current frame/focus posture;
- fail or emit an explicit projection-mismatch error if the file remains stale.

Why this matters:

- direct rendering success in memory did not guarantee correct persisted projection on disk in the observed incident.

### Phase D — keep scope separation between `frame advance` and `frame pin`

Goal:

- prevent future analysis or runtime messaging from blurring two distinct contracts.

Required outcomes:

- `frame advance` remains the path that must fully regenerate the required `QF.md` projection;
- `frame pin` should either:
  - remain explicitly bounded/header-sync only with honest messaging, or
  - be separately elevated later if policy wants full regeneration there too.

Why this matters:

- the active defect investigation was specifically about advance-path regeneration, and future remediation should preserve that distinction instead of muddying causality.

### Phase E — regression validation for the repaired path

Goal:

- prove that required projection regeneration is now stable under the same conditions that produced the stale `QF.md`.

Required validation slices:

1. run native frame advancement on a representative job lane;
2. verify `operations/tasks.json`, `QS.json`, and persisted `QF.md` agree on current frame posture;
3. verify the command fails closed if QF regeneration is intentionally broken or blocked;
4. verify the same contract from nested working directories where applicable, so root-resolution and projection persistence do not regress independently.

### Implementation target summary

If later implementation is authorized, the concrete preferred repair is:

- keep full QF regeneration in the `frame advance` path,
- make it mandatory rather than silent best-effort,
- add explicit stage-level failure signaling,
- and verify persisted projection parity before reporting successful advance.

That is the narrowest fix that matches the direct evidence gathered in this investigation.

### Planning outcome preserved for the active lane

For the Calamum lane specifically, this addendum preserves four practical truths:

1. the machine-readable state surfaces were healthy when the defect was observed;
2. the active frame-advance path does invoke the regenerator;
3. the renderer can produce the correct `qf3` projection from current authority inputs;
4. the unresolved problem is that required persisted QF regeneration is not currently enforced or verified strongly enough.

That preserved conclusion should keep future remediation work focused on the real defect instead of reopening already-refuted hypotheses.

## Audit-only closing note

This scratchpad is a supporting audit record for the active Calamum lane. It is not a first-order authority surface and does not mutate the job packet, lifecycle registry, or queststack. Current authority remains anchored to the first-order policy/SSOT corpus listed above.