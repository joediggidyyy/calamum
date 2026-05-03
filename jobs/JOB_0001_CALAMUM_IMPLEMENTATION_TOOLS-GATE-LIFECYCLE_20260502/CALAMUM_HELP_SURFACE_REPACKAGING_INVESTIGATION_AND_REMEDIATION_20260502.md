TL;DR: The `calamum -h` page is accurately reflecting the currently shipped standalone Calamum CLI, not a stale cache. The live package wired into `.venv-core` still exposes only the top-level `test` command family. The completed Calamum JOB_0001 lane closed a planning/scaffolding handoff for future `calamum monitor` / top-level `calamum project` parity; it did not ship those command families. Repackaging alone will not change the help page until the CLI route tree and support docs are updated and the package is rebuilt/reinstalled.

# Calamum help-surface repackaging investigation and remediation

## Classification

- Artifact class: `supporting investigation scratchpad`
- Authority posture: `derived/supporting only`
- Not lifecycle authority for status or execution state
- Related job: `calamum-job-0001-tools_gate_lifecycle-20260502`
- Recorded by: `ORACL-Prime`
- Recorded at (UTC): `2026-05-02`

## Question investigated

Why does `calamum -h` still show only:

- top-level `test`

when the Calamum upgrade was understood to be completed, and what remediation is actually required?

## Observed help surface

From the operator screenshot, the active help surface shows:

- usage: `calamum [-h] <command> ...`
- summary: `Calamum retained-evidence testing CLI for catalog definitions, project context, retained runs, and aggregate reports.`
- commands:
  - `test`
- examples:
  - `calamum test list`
  - `calamum test project current`
  - `calamum test reports list`

## Evidence collected

### 1) The live CLI code only registers top-level `test`

File:
- `projects/calamum/src/calamum/cli.py`

Observed implementation:
- root parser summary is set to `Calamum retained-evidence testing CLI for catalog definitions, project context, retained runs, and aggregate reports.`
- root command groups register only:
  - `test`
- nested routes under `test` include:
  - `project`
  - `runs`
  - `reports`

Implication:
- the screenshot matches the current parser implementation exactly
- there is no evidence that `monitor` or top-level `project` are already shipped in the parser

### 2) The shipped Calamum package entrypoint points at that same CLI module

File:
- `projects/calamum/pyproject.toml`

Observed packaging contract:
- distribution name: `calamum-test`
- console script:
  - `calamum = calamum.cli:main`

Implication:
- the standalone `calamum` executable is generated from `calamum.cli:main`
- if `calamum.cli` only exposes top-level `test`, repackaging the current code still yields the same help page

### 3) The editable package installed in the workspace venv is the Calamum child project

Terminal evidence:
- `pip show calamum-test`
- installed version: `0.2.0`
- editable project location: `C:\Users\joedi\Documents\CodeSentinel-1\projects\calamum`

Additional environment evidence:
- `.venv-core\Scripts\calamum.exe` exists

Implication:
- this is not a mystery external binary pointing somewhere unexpected
- the active console script is sourced from the child project already
- the package is present, but it is packaging the current parser shape, not a newer unshipped surface

### 4) The public project README still documents top-level `test` only

File:
- `projects/calamum/README.md`

Observed command-surface documentation:
- command surface sections are framed as:
  - `calamum test list`
  - `calamum test show <definition_id>`
  - `calamum test run <definition_id>`
  - `calamum test project ...`
  - `calamum test reports ...`
- quick-start examples likewise use `calamum test ...`

Implication:
- the shipped support docs agree with the current help page
- if the expectation was top-level `calamum project` or `calamum monitor`, the README has not yet been upgraded to present that as shipped behavior

### 5) Current policy/SSOT explicitly says only `calamum test ...` is presently shipped

Files:
- `docs/operations/ssot/JOBS_AND_EXECUTION_SSOT.md`
- `docs/policies/operations/OPERATIONS_POLICY/PP_OPS_PROTOCOL_POL_JOB_PIPELINE_AUTHORITY_AND_EXECUTION_ARTIFACTS_20260312.md`

Observed authority language:
- current shipped Calamum native lane is `calamum test ...`
- `calamum monitor ...` and `calamum project ...` are described as planned native families until shipped

Implication:
- the authoritative policy surfaces align with the observed help page
- the help page is not contradicting current SSOT

### 6) The completed Calamum JOB_0001 was a planning/scaffolding handoff, not proof that the new command families were implemented

Files:
- `projects/calamum/jobs/JOB_0001_CALAMUM_IMPLEMENTATION_TOOLS-GATE-LIFECYCLE_20260502/JOB.json`
- `projects/calamum/jobs/JOB_0001_CALAMUM_IMPLEMENTATION_TOOLS-GATE-LIFECYCLE_20260502/JOB.md`

Observed job content:
- objective: prepare the standalone Calamum monitor/project-evidence implementation lane for safe execution
- executive problem: current Calamum CLI is still centered on `calamum test`
- affected-system map explicitly states:
  - current state: only top-level `calamum test` is implemented; project and report commands are nested below `test`
  - target state: expose accepted top-level `calamum project` and `calamum monitor` families while preserving existing behavior
- job status is `completed`, but the readiness statement is about the planning frame stack being completed

Implication:
- the completed job closed the planning / handoff / scaffolding lane
- it did not itself prove that the product help surface had already been migrated and published
- the phrase "we completed the calamum upgrade" is therefore broader than the actual completed artifact set

## Root-cause assessment

The help page is not stale. It is current for the code and package that are actually installed.

The apparent mismatch comes from a scope/phase conflation:

1. **Completed work:**
   - the Calamum monitor/project-evidence planning job was completed
   - the future native grammar was accepted and documented as the target

2. **Not yet demonstrated as shipped in evidence gathered here:**
   - top-level `calamum project`
   - top-level `calamum monitor`
   - updated root help text that lists those families
   - upgraded README/support docs presenting those families as current shipped behavior
   - rebuilt/reinstalled package evidence showing the new surface live in `.venv-core`

In plain English: the roadmap/handoff was completed, not the operator-facing CLI migration itself.

## Repackaging conclusion

Repackaging is necessary only **after** the route tree and docs are updated.

Repackaging the current child project as-is would still produce:
- `calamum -h` with only top-level `test`

because that is what `calamum.cli:main` currently defines.

## Support-doc drift conclusion

There is a likely documentation expectation gap, but not the one shown in the screenshot.

- The screenshot is aligned with current shipped code and current Calamum README.
- The drift appears to be between:
  - planning/accepted-target language that treats `monitor` / top-level `project` as the intended architecture
  - and the still-shipped product/docs surface that remains `calamum test`-first

Any support docs that imply the new command families are already shipped should be updated to either:
- present them as planned/future-native until released, or
- be revised after the CLI actually ships those routes

## Recommended remediation sequence

### Immediate remediation packet

1. **Lock the truth statement**
   - Current shipped CLI: `calamum test ...`
   - Planned target families: `calamum monitor ...`, top-level `calamum project ...`

2. **Implement the missing route migration in product code**
   - update `projects/calamum/src/calamum/cli.py`
   - expose canonical top-level families required by the accepted architecture
   - decide explicit compatibility posture for nested legacy routes:
     - compat alias
     - retained nested helper
     - or bounded sunset path

3. **Update support docs in the same release lane**
   - `projects/calamum/README.md`
   - any Calamum security/help/usage docs touched by the route migration
   - any cross-project docs that presently overstate the shipped surface

4. **Rebuild/reinstall the child package into the active environment**
   - ensure `.venv-core` picks up the updated `calamum.cli:main`
   - validate the generated console script help after reinstall/build refresh

5. **Validate the help surfaces explicitly**
   - `calamum -h`
   - `calamum test -h`
   - `calamum project -h`
   - `calamum monitor -h`
   - plus any compatibility alias help/runtime warnings if retained

### Expected acceptance evidence

The remediation should not be considered complete until retained evidence shows at minimum:

- root help lists the shipped top-level command families
- README/examples match the root help truthfully
- compatibility behavior is documented and test-covered
- the rebuilt/reinstalled package in `.venv-core` exposes the same live surface the docs claim

## Bottom line

The screenshot is telling the truth.

What is missing is not a cache clear; it is the actual CLI migration + doc update + package refresh needed to make the accepted future Calamum grammar become the shipped present-tense product surface.

## Full remediation plan

This section converts the investigation into an execution-ready remediation program for the currently active blocker.

### Remediation objective

Ship the accepted standalone Calamum command-surface upgrade so that all of the following become simultaneously true:

- `calamum -h` exposes the shipped top-level families truthfully;
- the canonical product docs present the same surface the CLI actually ships;
- nested legacy routes remain either explicitly supported as compatibility aliases or explicitly retired with clear operator guidance;
- the rebuilt/reinstalled package in `.venv-core` resolves to the upgraded help surface;
- the active blocker can be retired because the operator-visible product now matches the accepted architecture.

### Blocker statement to clear

Current blocker:

- accepted target architecture exists in planning/handoff artifacts,
- but the shipped CLI, installed package, and support docs still present the pre-upgrade `calamum test`-first root surface.

Blocker-clear condition:

- the shipped Calamum child project exposes the upgraded top-level command grammar in live help output, and support docs + retained evidence validate the same present-tense surface.

## Execution strategy

### Phase 1 - freeze the canonical shipped-vs-target contract

Purpose:

- prevent implementation churn caused by mixing current truth, target truth, and compatibility language.

Required outcome:

- one explicit contract for what is shipped now,
- one explicit contract for what this remediation will ship,
- one explicit contract for legacy compatibility behavior.

Decisions to freeze before code mutation:

1. **Canonical top-level families to ship in this lane**
  - `calamum test`
  - `calamum project`
  - `calamum monitor`

2. **Legacy nested route posture**
  - retain `calamum test project ...` as a compatibility alias for a bounded transition window;
  - retain `calamum test reports ...` and `calamum test runs ...` only if still needed to protect existing workflows;
  - help and runtime output must indicate canonical replacement when a compat-alias path is used.

3. **Truthful authority wording**
  - until the upgraded surface is actually shipped, support docs must not describe `calamum project ...` or `calamum monitor ...` as already-live present-tense behavior;
  - once shipped, support docs and help output must switch together.

### Phase 2 - root CLI route migration

Primary target:

- `projects/calamum/src/calamum/cli.py`

Required implementation goals:

1. add top-level parser families for:
  - `project`
  - `monitor`
2. preserve top-level `test`
3. decide whether retained-evidence review remains temporarily available under:
  - `calamum test runs ...`
  - `calamum test reports ...`
  - and/or is surfaced canonically elsewhere during this same lane
4. update root help summary/examples to reflect the actual upgraded route tree
5. ensure compat-alias routes emit replacement guidance rather than silently pretending nothing changed

Minimum viable command shape to land in this remediation:

- `calamum -h`
- `calamum test -h`
- `calamum project -h`
- `calamum monitor -h`

Minimum viable `project` scope for this lane:

- `calamum project register`
- `calamum project set <project>` or approved canonical equivalent
- `calamum project current`
- `calamum project validate`
- `calamum project list`
- `calamum project show <project>`

Minimum viable `monitor` scope for this lane:

- ship the command family and help scaffolding truthfully;
- if substantive monitor operations are not ready in the same implementation slice, help output must present the currently implemented monitor subgroup surface accurately instead of implying hidden completeness.

### Phase 3 - project/evidence route normalization

Primary purpose:

- move project-context behavior out of the nested `test` mental model so the CLI hierarchy matches the accepted architecture.

Implementation targets likely involved:

- `projects/calamum/src/calamum/cli.py`
- `projects/calamum/src/calamum/projects.py`
- `projects/calamum/src/calamum/render.py`
- `projects/calamum/src/calamum/layout.py`
- `projects/calamum/src/calamum/api.py`

Required outcome:

- the existing project-context machinery remains reusable,
- but canonical operator entry becomes top-level `calamum project ...`.

Compatibility requirement:

- existing nested project flows must either continue to work as aliases or fail with an explicit canonical replacement packet;
- silent breakage is not acceptable.

### Phase 4 - monitor-family scaffolding delivery

Primary purpose:

- ensure the root help page stops lying by omission once `monitor` is part of the accepted shipped surface.

Implementation targets likely involved:

- `projects/calamum/src/calamum/cli.py`
- any new monitor-facing modules introduced in `projects/calamum/src/calamum/`
- `projects/calamum/tests/test_cli.py`

Required outcome:

- `calamum monitor -h` exists and is truthful;
- help text must not over-claim adapter readiness or backend availability;
- monitor help should present Calamum-native nouns, not backend tool names.

Important constraint:

- if monitor execution features are only partially ready in this remediation, ship honest scaffolding and bounded subcommands rather than inflated future tense.

### Phase 5 - documentation and support-surface synchronization

Primary docs to update in the same release lane:

- `projects/calamum/README.md`
- `projects/calamum/SECURITY.md` if command usage or privileged monitor behavior is described there
- any Calamum-local help/usage/support docs touched by the route migration

Secondary/supporting docs to audit after product docs are corrected:

- cross-project references that may currently imply the upgraded route tree is already shipped
- only the surfaces that would become misleading after the product CLI lands should be updated in the same remediation pass

Documentation rules:

1. README examples must match live help output exactly
2. present-tense wording only for actually shipped commands
3. planned/future-native wording only for still-unshipped families or subgroups
4. compatibility aliases must be described as aliases, not as equal canonical routes

### Phase 6 - packaging and environment refresh

Purpose:

- ensure the live console script in `.venv-core` reflects the upgraded route tree rather than stale editable/install assumptions.

Targets / checks:

- `projects/calamum/pyproject.toml`
- `.venv-core` editable install state
- generated `calamum.exe` shim behavior after reinstall/refresh

Required actions in this lane:

1. verify packaging metadata remains correct:
  - distribution: `calamum-test`
  - runtime CLI: `calamum`
2. rebuild or reinstall the child project into `.venv-core`
3. validate that the live executable now renders the upgraded help surface

Important constraint:

- packaging refresh happens **after** CLI/doc changes land, not before.

### Phase 7 - validation and retained evidence

This repo’s validation contract requires more than optimistic eyeballing.

Validation must cover at least:

1. **CLI parser/help validation**
  - root help
  - top-level family help
  - compatibility-alias behavior

2. **Regression validation for existing behavior**
  - current test-definition listing/show/run flows must still function
  - project context resolution must remain deterministic
  - report/run review paths must not silently disappear

3. **Packaging/live-command validation**
  - the executable in `.venv-core` must render the same upgraded surface documented in README

4. **Retained evidence / consolidated validation posture**
  - validation should be orchestrated through `calamum test` per repo contract where applicable
  - retain command outputs/evidence proving both parser truth and compatibility behavior

Candidate validation file targets:

- `projects/calamum/tests/test_cli.py`
- any additional tests covering route migration and compatibility warnings

Minimum acceptance evidence to retain:

- passing CLI route/help tests
- retained output for `calamum -h`
- retained output for `calamum project -h`
- retained output for `calamum monitor -h`
- retained output for at least one preserved legacy alias invocation if aliases are retained
- retained output showing README/examples match the live executable behavior

## File-level remediation map

### Must-touch surfaces

- `projects/calamum/src/calamum/cli.py`
- `projects/calamum/README.md`
- `projects/calamum/tests/test_cli.py`

### Likely-touch surfaces

- `projects/calamum/src/calamum/projects.py`
- `projects/calamum/src/calamum/render.py`
- `projects/calamum/src/calamum/layout.py`
- `projects/calamum/src/calamum/api.py`
- `projects/calamum/SECURITY.md`
- `projects/calamum/pyproject.toml` only if packaging metadata or extras actually need correction

### Audit-only surfaces

- `docs/operations/ssot/JOBS_AND_EXECUTION_SSOT.md`
- `docs/policies/operations/OPERATIONS_POLICY/PP_OPS_PROTOCOL_POL_JOB_PIPELINE_AUTHORITY_AND_EXECUTION_ARTIFACTS_20260312.md`

These authority surfaces already appear truthful for present state and should only be changed if the newly shipped surface requires a present-tense wording update after implementation is complete.

## Recommended implementation order

1. freeze compatibility and command-family decisions
2. update `cli.py` root route tree and help renderers
3. wire top-level `project` family onto existing project handlers
4. add truthful `monitor` family scaffolding
5. add/adjust route tests in `tests/test_cli.py`
6. update README/support docs to match shipped help
7. rebuild/reinstall the Calamum child package in `.venv-core`
8. run validation and capture retained evidence
9. audit any remaining docs that overstate or understate the shipped surface

## Compatibility policy recommendation

Recommended policy for this remediation:

- canonical after ship:
  - `calamum project ...`
  - `calamum monitor ...`
- retained compat aliases for one bounded transition lane:
  - `calamum test project ...`
  - `calamum test reports ...`
  - `calamum test runs ...`

Required alias behavior:

- help/runtime output should indicate canonical replacement
- aliases should remain functional only as long as needed to protect active consumers
- once sunset timing is approved, aliases can move to a more explicit retirement posture

## Exit criteria for the blocker

The blocker remains active until all of the following are true:

1. `calamum -h` shows the upgraded top-level route tree
2. `calamum.cli:main` is the live source of that upgraded route tree
3. `.venv-core` executable behavior matches the upgraded source tree
4. `projects/calamum/README.md` matches live help output truthfully
5. compatibility posture is documented and test-covered
6. validation evidence exists for root help, family help, and preserved legacy behavior

## Immediate next action packet

If remediation starts now, the first concrete mutation pass should do exactly this:

1. update `projects/calamum/src/calamum/cli.py` to add top-level `project` and truthful `monitor` routing;
2. preserve or explicitly classify legacy nested routes as compatibility aliases;
3. update `projects/calamum/tests/test_cli.py` for root-help and alias-parity coverage;
4. update `projects/calamum/README.md` to match the shipped command grammar;
5. refresh the editable install in `.venv-core` and validate the live help output.

That is the minimum full-path remediation needed to retire the active blocker honestly.

## Implementation checklist

Use this checklist as the live execution driver for the remediation lane.

### A. Contract freeze and pre-mutation decisions

- [ ] Confirm the canonical shipped top-level families for this lane:
  - [ ] `calamum test`
  - [ ] `calamum project`
  - [ ] `calamum monitor`
- [ ] Confirm the canonical verb set for the minimum viable `project` surface.
- [ ] Confirm the minimum viable `monitor` help surface to ship in this lane.
- [ ] Decide compatibility posture for nested legacy routes:
  - [ ] `calamum test project ...`
  - [ ] `calamum test runs ...`
  - [ ] `calamum test reports ...`
- [ ] Freeze whether compatibility routes remain fully functional aliases or transitional wrappers with runtime guidance.
- [ ] Freeze the help/runtime wording for canonical replacements so compat behavior is consistent.

### B. Root CLI route migration

- [ ] Update `projects/calamum/src/calamum/cli.py` root parser to expose the upgraded top-level route tree.
- [ ] Add top-level `project` parser wiring.
- [ ] Add top-level `monitor` parser wiring.
- [ ] Preserve top-level `test` parser wiring.
- [ ] Update root help summary to describe the shipped CLI truthfully.
- [ ] Update root help groups/examples so they reflect the new top-level family split.
- [ ] Ensure root help no longer implies that `project` and reporting are only nested below `test`.

### C. Project-surface promotion

- [ ] Reuse existing project-context handlers for canonical top-level `calamum project ...` routing.
- [ ] Verify support for the minimum viable project commands:
  - [ ] `register`
  - [ ] `set` or approved canonical equivalent
  - [ ] `current`
  - [ ] `validate`
  - [ ] `list`
  - [ ] `show`
- [ ] Confirm help text for `calamum project -h` is truthful and operator-friendly.
- [ ] Ensure project-context resolution precedence remains unchanged unless explicitly approved.

### D. Monitor-family scaffolding

- [ ] Add a truthful top-level `calamum monitor` family.
- [ ] Ensure `calamum monitor -h` renders successfully.
- [ ] Keep operator-facing monitor nouns Calamum-native rather than backend-tool-named.
- [ ] If the monitor lane is only partially implemented in this pass, make the help surface explicitly bounded rather than overstated.
- [ ] Confirm monitor help does not imply backend availability or live-readiness unless that behavior truly exists.

### E. Compatibility handling

- [ ] Decide which nested `test` routes remain temporarily supported.
- [ ] Implement canonical replacement guidance for every retained compatibility route.
- [ ] Verify compat-alias help/runtime behavior is consistent with repo deprecation rules.
- [ ] Ensure no existing supported path silently disappears without an explicit canonical replacement.

### F. Test and validation updates

- [ ] Update `projects/calamum/tests/test_cli.py` for the new root route tree.
- [ ] Add root-help assertions covering top-level command families.
- [ ] Add coverage for `calamum project -h`.
- [ ] Add coverage for `calamum monitor -h`.
- [ ] Add coverage for retained compatibility aliases if they remain supported.
- [ ] Add regression coverage ensuring existing `calamum test` behavior still works.
- [ ] Confirm test coverage distinguishes canonical routes from compat aliases.

### G. Documentation synchronization

- [ ] Update `projects/calamum/README.md` so examples match the shipped CLI.
- [ ] Update command-surface sections to reflect the new top-level families.
- [ ] Update quick-start examples to reflect the new canonical grammar.
- [ ] Mark any retained nested `test` routes as compatibility aliases if they remain documented.
- [ ] Audit `projects/calamum/SECURITY.md` for any help/usage/security text impacted by the route migration.
- [ ] Audit any immediately adjacent Calamum-local docs that would become misleading after ship.

### H. Packaging and environment refresh

- [ ] Confirm `projects/calamum/pyproject.toml` still exposes the correct console script:
  - [ ] `calamum = calamum.cli:main`
- [ ] Reinstall or refresh the editable `projects/calamum` package into `.venv-core` after code/doc changes land.
- [ ] Confirm `.venv-core\Scripts\calamum.exe` resolves to the upgraded route tree.
- [ ] Verify packaging refresh happens after implementation changes, not before.

### I. Live surface verification

- [ ] Capture and review `calamum -h`.
- [ ] Capture and review `calamum test -h`.
- [ ] Capture and review `calamum project -h`.
- [ ] Capture and review `calamum monitor -h`.
- [ ] Capture and review at least one retained compatibility route if aliases remain supported.
- [ ] Confirm README examples match the live help output exactly.

### J. Blocker-close verification

- [ ] Confirm the root help page now reflects the accepted shipped grammar.
- [ ] Confirm the live executable in `.venv-core` matches source-tree expectations.
- [ ] Confirm docs and help are synchronized.
- [ ] Confirm compatibility behavior is documented and test-covered.
- [ ] Confirm retained evidence exists for the upgraded command surface.
- [ ] Confirm the previous help-surface mismatch blocker can be retired truthfully.

### K. Final operator-facing completion packet

- [ ] Summarize what changed in the CLI route tree.
- [ ] Summarize any compatibility aliases retained and their intended sunset posture.
- [ ] Summarize packaging refresh results.
- [ ] Summarize validation results and retained evidence pointers.
- [ ] State explicitly whether the blocker is cleared or what residual gap remains.

## Release/version and PyPI package-name assessment

### Correction to prior framing

Because `calamum-test` is already published on PyPI, is already consumed as a dependency by other projects, and has nontrivial download history, there is already a real public contract in force.

What remains flexible is **maturity signaling**, not whether a contract exists at all.

- Publishing to PyPI created an external compatibility surface.
- Downstream dependency use strengthens that surface.
- Pre-`1.0.0` versioning still allows change, but it does **not** erase operator/downstream compatibility responsibility.

Therefore, the more accurate statement is:

- `1.0.0` is **not required** for the package to have a public contract;
- `1.0.0` would instead signal a stronger stability promise and a more explicit release-discipline milestone.

### Version recommendation adjustment

Given current metadata:

- distribution: `calamum-test`
- current version: `0.2.0`

and given the newly shipped top-level CLI family expansion, the recommended next release remains:

- `0.3.0`

Reasoning:

- too large for a patch release;
- still compatible with ongoing pre-`1.0` evolution;
- signals meaningful public-surface growth without claiming that all CLI families are now frozen permanently.

If a stronger stability declaration is desired only after an additional hardening lane, then:

- ship this remediation as `0.3.0`;
- reserve `1.0.0` for the later milestone where package identity, CLI contract, compatibility window, and release policy are all explicitly frozen.

### PyPI distribution-name reality check

Current published distribution name:

- `calamum-test`

Current runtime / console identity:

- import package: `calamum`
- console script: `calamum`

Assessment:

- the published PyPI distribution name cannot be meaningfully "renamed in place" for existing releases;
- if `calamum-test` is already the installed dependency name used by downstream projects, it is the live distribution identity that must be supported for continuity;
- this is awkward, but it is **not** fatal.

More precise conclusion:

- it is too late to pretend the released distribution name was something else;
- it is **not** too late to improve the long-term naming posture.

### Practical options from here

#### Option A - keep `calamum-test` as the canonical PyPI distribution

Use when:

- minimizing downstream disruption is the top priority.

Recommended posture:

- keep publishing the distribution as `calamum-test`;
- keep the runtime/import/CLI identity as `calamum`;
- document the split explicitly in README and release notes.

Pros:

- no dependency-coordinate churn for downstreams;
- lowest operational risk.

Cons:

- permanent naming mismatch between PyPI distribution and operator-facing product name.

#### Option B - introduce a new canonical `calamum` distribution later, with a transition plan

Use when:

- long-term naming correctness matters enough to justify migration work.

Recommended posture:

- publish a new `calamum` distribution when available/appropriate;
- keep `calamum-test` alive temporarily as a compatibility/transition distribution if feasible;
- provide explicit downstream migration instructions and a bounded transition window.

Pros:

- eventually aligns package-install name with the actual product/CLI identity.

Cons:

- requires transition management;
- may be impossible to use the exact `calamum` name if it is unavailable on PyPI.

### Recommendation

Recommended near-term lane:

1. treat `calamum-test` as the authoritative published distribution for the upcoming release;
2. publish this command-surface remediation as `0.3.0`;
3. explicitly document that:
  - install/distribution name is `calamum-test`;
  - runtime command is `calamum`;
4. defer any package-name migration to a separate, explicit transition plan rather than mixing it into this CLI remediation lane.

This keeps the present release honest, minimizes downstream churn, and leaves room for a later naming-correction strategy if the ecosystem cost is justified.

## Repackaging and publishing plan for the upcoming PyPI release

### TL;DR

The correct near-term release lane is:

- publish the upgraded CLI as `calamum-test` version `0.3.0`;
- keep runtime/import/operator identity as `calamum`;
- add a real `--version` surface;
- make version/report/help/doc/package metadata converge from one governed source;
- regenerate, not hand-edit, package metadata and publish-facing generated surfaces;
- validate editable install, wheel install, sdist install, TestPyPI, and final PyPI with retained evidence.

### Grounded affected-system map for this lane

Based on the current repository state, the repackaging/publish lane touches at least these surface classes.

#### A. Canonical version and package identity sources

- `projects/calamum/pyproject.toml`
- `projects/calamum/src/calamum/__init__.py`
- live package metadata generated into `src/calamum_test.egg-info/PKG-INFO`

#### B. CLI and terminal-facing surfaces

- `projects/calamum/src/calamum/cli.py`
- `projects/calamum/src/calamum/render.py`
- `projects/calamum/tests/test_cli.py`
- live help and command output shown via `calamum.exe`

#### C. User-facing documentation surfaces

- `projects/calamum/README.md`
- `projects/calamum/SECURITY.md`
- `projects/calamum/CONTRIBUTING.md`
- any future release notes / publish notes used in the standalone repo lane

#### D. Generated / publish-adjacent metadata and output surfaces

- `projects/calamum/src/calamum_test.egg-info/PKG-INFO`
- `projects/calamum/dist/`
- retained run and report outputs under:
  - `projects/calamum/runs/`
  - `projects/calamum/reports/`
  - local `.calamum/generated/...` outputs when used during validation

#### E. Planning / supporting record surfaces that should reflect the decision

- this active remediation document
- existing local planning docs under `projects/calamum/planning/`

### Release objective for this lane

Ship a professional PyPI update where all of the following are simultaneously true:

- the package version is consistent everywhere it is supposed to be consistent;
- `calamum --version` is available and trustworthy;
- install name vs runtime name are documented explicitly;
- README/help/examples/screenshots/terminal snippets match the actual shipped CLI;
- generated packaging metadata is freshly regenerated from source rather than stale;
- wheels and sdists exclude local-only noise and include intended publishable assets only;
- TestPyPI and PyPI install flows both work in clean environments;
- the release can be consumed by downstream projects without ambiguity.

## Phase 1 - freeze version and identity authority

### Recommended version for this release

- target release version: `0.3.0`

### Recommended identity statement to freeze

- PyPI distribution / dependency name: `calamum-test`
- import package name: `calamum`
- console command: `calamum`
- human-facing product name in prose: `Calamum Test`

### Critical packaging recommendation

This release should stop treating version data as duplicated folklore.

Current observed duplication:

- `pyproject.toml` contains `version = "0.2.0"`
- `src/calamum/__init__.py` contains `__version__ = "0.2.0"`

Recommended remediation:

- define one canonical version authority and make the other surfaces derive from it;
- avoid manual multi-file version drift in future releases.

Recommended implementation shape:

1. keep `src/calamum/__init__.py` as the runtime-readable `__version__` source; and
2. make packaging metadata in `pyproject.toml` read that value dynamically if practical for the chosen build flow.

If dynamic packaging metadata is not adopted in this lane, then the release checklist must explicitly require synchronized updates in both places plus verification after build.

## Phase 2 - add a real `--version` operator surface

### Requirement

Add top-level support for:

- `calamum --version`
- optionally `calamum version` only if you intentionally want a subcommand form too

### Recommended behavior

`calamum --version` should print a concise professional line, for example:

- `calamum 0.3.0`

Optional richer shape if the naming split should be explicit:

- `calamum 0.3.0 (distribution: calamum-test)`

Recommended default:

- keep terminal output concise;
- reserve the more verbose name-split explanation for README / release notes rather than making the normal version output noisy.

### Technical recommendation

Prefer a runtime lookup path that stays honest after installation:

1. first try package metadata for installed-distribution truth;
2. fall back to `calamum.__version__` for editable/dev scenarios.

This avoids a version surface that lies after packaging mistakes.

### Required validation

- direct function-level tests in `tests/test_cli.py`
- live console-script verification via `.venv-core\Scripts\calamum.exe --version`
- wheel-install verification in a clean environment
- sdist-install verification in a clean environment

## Phase 3 - scan and synchronize all version mentions across `projects/calamum/`

### Why this needs a formal plan

The current subtree contains both canonical version sources and many incidental mentions, including generated metadata and retained evidence. A release-quality sweep must separate:

- **source-of-truth surfaces to update**
- **generated surfaces to regenerate**
- **historical evidence surfaces to preserve, not hand-edit**

### Cross-validated search requirement

Use **two methods**, not one.

#### Method 1 - scripted release scan (recommended as the authoritative audit)

Create and run a dedicated release-audit script that walks `projects/calamum/` and classifies hits into buckets such as:

- canonical version sources
- user-facing docs/examples
- generated package metadata
- retained evidence / historical outputs
- ignored/local-only noise

Minimum search tokens:

- `0.2.0`
- `0.3.0` after bump
- `__version__`
- `version =`
- `calamum-test`
- `calamum --version`

Recommended output:

- JSON summary for machine review
- Markdown summary for operator review

#### Method 2 - independent cross-check using repo text search

Cross-validate the script results with one independent method, for example:

- VS Code workspace search; or
- `git grep`; or
- repo text search via the editor search panel.

Do not rely on the script alone. The second method is there to catch:

- bad exclude rules
- unanticipated file classes
- generated metadata that the script skipped incorrectly

### Update policy by bucket

#### Bucket A - update directly

Update these in source when the version changes:

- `pyproject.toml`
- `src/calamum/__init__.py`
- README release/version references
- explicit version examples in docs when they exist
- CLI tests asserting version output

#### Bucket B - regenerate, do not hand-edit

Regenerate these from the updated source/build flow:

- `src/calamum_test.egg-info/PKG-INFO`
- `dist/*`
- any package metadata snapshots emitted during build

#### Bucket C - preserve as historical evidence unless the lane explicitly re-baselines them

Do **not** casually hand-edit historical retained evidence or old generated reports just to make them match the new version. That would rewrite history.

Examples:

- old files under `runs/`
- old files under `reports/generated/`
- old run/report Markdown and JSON payloads proving prior release/test behavior

If a user-facing publish lane truly requires refreshed terminal/report snapshots, generate fresh release evidence under a new release-validation run rather than mutating old evidence in place.

## Phase 4 - update all user-facing surfaces

### README and primary docs

At minimum, review and update:

- `README.md`
- `SECURITY.md`
- `CONTRIBUTING.md`

The README should explicitly state, in one clean section:

- install from PyPI as `calamum-test`
- run as `calamum`
- check installed version with `calamum --version`

### Help and terminal-facing text

Review for polish and consistency across:

- root help summary
- examples in help pages
- no-go packets
- section headings and rendered titles
- any output that still reads like seed scaffolding or overly internal developer phrasing

### Terminal output data and retained artifacts

User-facing generated outputs that may need **fresh regeneration** for the new release include:

- sample run Markdown/JSON used as demonstration material
- report pairs used as release/publish evidence
- any checked-in snippets or screenshots sourced from older command output

Important rule:

- regenerate fresh release evidence for publish-facing documentation;
- do not falsify old retained evidence.

### Specific current hotspots already identified

Observed surfaces that should be reviewed in this lane include:

- `src/calamum_test.egg-info/PKG-INFO` (generated metadata)
- `runs/.../report.md` and `report.json` historical outputs mentioning older command/review strings
- `reports/generated/...` historical outputs mentioning `calamum-test` targets and old aggregates

These are not all necessarily direct-edit candidates, but they must be classified intentionally before release.

## Phase 5 - packaging hygiene and build-surface cleanup

### Build-content audit

Before publishing, verify the sdist and wheel include only intended publishable content.

Explicitly inspect whether the release artifacts include or exclude the right things for:

- `assets/branding/`
- `README.md`
- `LICENSE`
- `SECURITY.md`
- package source under `src/calamum/`

and exclude local or irrelevant surfaces such as:

- `.env`
- `.agent_session/`
- `logs/`
- retained local run/report evidence
- local planning surfaces meant to remain ignored
- stale build outputs

### Professional packaging checks

Required checks for a polished release:

- build fresh `sdist`
- build fresh `wheel`
- run `twine check`
- inspect the built artifact contents directly
- verify the README long description renders cleanly
- verify image paths still work or degrade acceptably on PyPI
- verify homepage / repository URLs and classifiers

### Additional recommended metadata checks

Review whether the following should be present/updated for professionalism:

- project URLs (`Homepage`, `Repository`, `Issues`, `Documentation` if available)
- keywords
- supported Python classifiers up to the version actually validated
- console-script metadata
- optional-dependency clarity

## Phase 6 - downstream-safe validation matrix

### Required validation classes

This release should preserve the three-lane Calamum validation posture plus package-install validation.

#### A. `pytest`

- unit/regression suite
- especially CLI tests for `--version`, help, monitor/project routes, and package-name wording

#### B. `sandbox_test`

- build/install in clean virtual environments
- wheel smoke install
- sdist smoke install
- TestPyPI smoke install if used

#### C. `empirical_test`

- operator-facing command checks:
  - `calamum --version`
  - `calamum -h`
  - `calamum project -h`
  - `calamum monitor -h`
  - at least one end-to-end run/report flow

#### D. Downstream dependency confidence check

Because Calamum is already a required dependency for other projects, add at least one validation step that simulates how a downstream consumer will see it after publish:

- clean install from built artifact;
- import `calamum` in Python;
- call a stable facade function from `calamum.api`;
- run `calamum --version`;
- run one CLI smoke command.

## Phase 7 - TestPyPI and PyPI execution plan

### Recommended publish sequence

1. finalize source changes and version bump
2. run the cross-validated version sweep
3. run tests
4. build fresh artifacts
5. run `twine check`
6. inspect artifact contents
7. publish to TestPyPI first
8. install from TestPyPI into a clean environment and smoke test
9. publish to PyPI
10. install from PyPI into a clean environment and smoke test again
11. record exact artifact hashes, version, and install evidence

### Publish-mode note

Choose and document one of:

- Trusted Publishing
- token-based publishing fallback

The release lane should not depend on ad hoc memory for publication credentials or authority.

## Phase 8 - release notes and professional presentation

### Required release-note content

The release notes / publish summary should explicitly include:

- release version: `0.3.0`
- install name on PyPI: `calamum-test`
- runtime command: `calamum`
- major user-facing changes:
  - top-level `project`
  - top-level `monitor`
  - `--version`
- compatibility note for retained `calamum test project ...` alias behavior if still supported
- any known bounded limitations of the current monitor scaffold

### Professional polish checklist

- confirm branding assets render correctly
- confirm README top section is clean and not overly internal
- confirm no obvious seed-placeholder language remains where it would look amateurish on PyPI
- confirm examples are copy-paste accurate
- confirm there is a concise install + verify path near the top of README

## Phase 9 - concrete execution checklist for this publish lane

### A. Version and identity

- [ ] Freeze release version as `0.3.0`
- [ ] Freeze identity statement: install `calamum-test`, run `calamum`
- [ ] Choose single-source version authority
- [ ] Update canonical version source(s)

### B. CLI version surface

- [ ] Add `calamum --version`
- [ ] Decide concise output format
- [ ] Add CLI tests for version output
- [ ] Verify console-script version output live

### C. Version sweep and cross-validation

- [ ] Run scripted version/name scan across `projects/calamum/`
- [ ] Run one independent search method as cross-check
- [ ] Classify hits into direct-update vs regenerate vs preserve
- [ ] Update direct-edit source surfaces
- [ ] Regenerate generated metadata surfaces

### D. User-facing surface sync

- [ ] Update README install/runtime/version guidance
- [ ] Update SECURITY/CONTRIBUTING if version/install guidance appears there
- [ ] Review help summaries/examples for polish
- [ ] Refresh any publish-facing terminal output snippets with fresh evidence

### E. Packaging quality gate

- [ ] Build fresh wheel and sdist
- [ ] Run `twine check`
- [ ] Inspect artifact contents
- [ ] Confirm README renders correctly on package index
- [ ] Confirm publishable assets are included and local-only noise is excluded

### F. Validation

- [ ] Run `pytest`
- [ ] Run Calamum-governed validation via `calamum test`
- [ ] Smoke test editable install
- [ ] Smoke test wheel install in clean env
- [ ] Smoke test sdist install in clean env
- [ ] Validate downstream import + CLI behavior in clean env

### G. Publication

- [ ] Publish to TestPyPI
- [ ] Clean-install and smoke test from TestPyPI
- [ ] Publish to PyPI
- [ ] Clean-install and smoke test from PyPI
- [ ] Record version, artifact hashes, and verification evidence

## Recommended immediate next implementation slice after planning

When this planning lane turns into mutation/execution, the tightest first slice is:

1. add `--version` and tests;
2. establish single-source version authority;
3. update README install/runtime/version guidance;
4. run the scripted + independent version sweep;
5. classify generated/historical surfaces before touching any publish-facing artifacts.

That sequence reduces release-risk fastest while keeping the publish lane honest and professional.

## Repo-state validation of the repackaging and publishing plan

### Validation result

The publishing plan is **substantively aligned** with the current repo state and the Calamum project goals, but it needs a few explicit execution notes to stay fully grounded in what is actually present on disk.

### What is already validated as true

- the current published/distribution identity is still `calamum-test`;
- the runtime/import/CLI identity is still `calamum`;
- the current source version is still `0.2.0` in both:
  - `pyproject.toml`
  - `src/calamum/__init__.py`
- top-level `project` and `monitor` CLI families are already implemented in source;
- `src/calamum/__main__.py` delegates to `calamum.cli.main`, so adding `--version` in the CLI path will cover both console-script and `python -m calamum` execution paths;
- `tests/test_cli.py` already exists and is the correct primary surface for `--version` regression coverage;
- branding assets already exist under `assets/branding/` and can support polished package presentation;
- stale built artifacts already exist in `dist/`:
  - `calamum_test-0.2.0-py3-none-any.whl`
  - `calamum_test-0.2.0.tar.gz`
- generated package metadata already exists in `src/calamum_test.egg-info/PKG-INFO` and therefore must be treated as regenerated output, not a hand-maintained source file.

### Gaps the plan must explicitly account for

#### 1. No live `--version` surface yet

Validated state:

- `--version` is planned but not yet implemented in the CLI source.

Implication:

- the release cannot yet satisfy the desired professional install/verify path.

#### 2. README still lacks a polished PyPI install/verify section

Validated state:

- current README shows editable-install developer flow (`python -m pip install -e .[dev]`), but not a clear PyPI install + verify block for downstream users.

Implication:

- the package can publish successfully while still feeling unpolished or ambiguous to operators unless this is corrected.

#### 3. No standalone release-notes / changelog surface is present in `projects/calamum/`

Validated state:

- no `CHANGELOG*` or `RELEASE*` file was found under the Calamum subtree.

Implication:

- the release lane needs an explicit operator-facing release-notes artifact or changelog update rather than assuming one already exists.

#### 4. `pyproject.toml` does not yet advertise richer publish metadata

Validated state:

- no `project.urls`, `keywords`, or `dynamic` metadata is currently present.

Implication:

- the package will still build, but the professional-publication goal is not fully met until metadata is reviewed and improved.

#### 5. Historical run/report outputs exist and should not be rewritten in place

Validated state:

- older retained outputs under `runs/` and `reports/generated/` include `0.2.0`-era / pre-release-style content and `calamum-test` references.

Implication:

- the plan is correct to classify these as preserve-or-regenerate surfaces;
- fresh release evidence should be generated for publish-facing documentation instead of mutating old evidence.

### Validation against project goals

The plan is aligned with the project goals preserved in the Calamum planning corpus:

- preserve `calamum-test` as the dependency-grade published distribution for continuity;
- preserve `calamum` as the runtime/operator-facing surface;
- improve professional standalone packaging quality;
- keep user-facing docs and live CLI truth synchronized;
- validate package installability for downstream dependency use;
- preserve retained-evidence discipline rather than editing historical outputs into marketing material.

The only meaningful repo-state additions needed were:

- explicit cleanup/regeneration of stale `dist/` outputs;
- explicit treatment of `egg-info` as generated output;
- explicit addition of a release-note/changelog surface;
- explicit metadata-hardening tasks in `pyproject.toml`.

## Repo-validated execution checklist for the publish lane

Use this checklist as the concrete execution driver.

### A. Freeze version, identity, and release posture

- [x] Validate current published/distribution identity: `calamum-test`
- [x] Validate current runtime/import identity: `calamum`
- [x] Validate current source version is `0.2.0`
- [x] Freeze release version as `0.3.0`
- [x] Freeze exact version-output format for `calamum --version`
- [x] Decide whether version authority becomes dynamic or remains synchronized manually for this release

### B. Implement version surface

- [x] Add top-level `--version` handling in `src/calamum/cli.py`
- [x] Use `calamum.__version__` as the canonical CLI version source for this release
- [x] Confirm `python -m calamum --version` also works through `__main__.py`
- [x] Add `tests/test_cli.py` coverage for version output
- [x] Verify live console-script output from `.venv-core\Scripts\calamum.exe --version`

### C. Update canonical version sources

- [x] Update `projects/calamum/pyproject.toml` to `0.3.0`
- [x] Update `projects/calamum/src/calamum/__init__.py` to `0.3.0`
- [x] If dynamic version metadata is adopted, wire and verify it correctly
- [x] Re-run a source-level consistency check after the bump

### D. Run the cross-validated version/name sweep

- [x] Run a dedicated scripted release scan across `projects/calamum/`
- [x] Cross-check with a second method (`git grep` or VS Code search)
- [x] Classify every relevant hit into:
  - [x] direct-update source
  - [x] regenerate-only metadata/build output
  - [x] preserve-as-historical evidence
- [x] Record the scan result in release evidence

### E. Update user-facing source surfaces

- [x] Update `README.md` with a top-level PyPI install/verify section
- [x] Explicitly document:
  - [x] install name on PyPI: `calamum-test`
  - [x] runtime command: `calamum`
  - [x] version check: `calamum --version`
- [x] Review `SECURITY.md` for any packaging/install wording that should be tightened
- [x] Review `CONTRIBUTING.md` for release-hygiene wording that should reference the polished publish flow
- [x] Review CLI help summaries/examples for professional tone and copy-paste accuracy

### F. Add missing release-facing documentation

- [x] Create or update a Calamum-local release-notes / changelog surface
- [x] Record the `0.3.0` command-surface upgrade in that release-facing surface
- [x] Include the install/runtime name split in release notes
- [x] Include compatibility notes for retained alias routes if they remain supported

### G. Harden publish metadata

- [x] Review and add `project.urls` in `pyproject.toml`
- [x] Review and add `keywords` if useful
- [x] Review classifier completeness against actually validated Python versions
- [x] Review whether dynamic metadata should be declared explicitly if adopted
- [x] Confirm long-description / README packaging behavior is intentional

### H. Clean and regenerate build metadata

- [x] Remove or replace stale `dist/0.2.0` artifacts before the fresh build
- [x] Regenerate `src/calamum_test.egg-info/PKG-INFO` through the build/install flow
- [x] Confirm no stale build metadata survives into the release evidence bundle
- [x] Verify the rebuilt metadata reflects `0.3.0`

### I. Preserve history, regenerate proof

- [x] Validate that historical outputs exist under `runs/` and `reports/generated/`
- [x] Do **not** hand-edit historical retained evidence to match the new release
- [x] Generate fresh release-validation outputs for any publish-facing snippets or screenshots
- [ ] If terminal output is quoted in docs, regenerate it from the fresh release candidate

### J. Validation matrix

- [x] Run `pytest` for Calamum
- [x] Run Calamum-governed validation via `calamum test`
- [x] Verify editable-install behavior
- [x] Verify clean wheel-install behavior
- [x] Verify clean sdist-install behavior
- [x] Verify downstream dependency use:
  - [x] `import calamum`
  - [x] stable facade call from `calamum.api`
  - [x] `calamum --version`
  - [x] one CLI smoke command

### K. Packaging quality gate

- [x] Build fresh sdist
- [x] Build fresh wheel
- [x] Run `twine check`
- [x] Inspect artifact contents directly
- [x] Confirm publishable assets are present
- [x] Confirm local-only noise is excluded
- [x] Confirm README renders professionally on the package index

### L. Publication execution

Recovered canonical publication lane from governance artifacts in this session:

- the repo's historical publication guidance uses the persisted user credential file path (`~/.pypirc` on this machine) rather than transient env-var injection for Twine authentication
- names-only verification showed `C:\Users\joedi\.pypirc` exists and contains the expected `distutils`, `testpypi`, and `pypi` sections with the expected credential keys
- the earlier failure came from bypassing that canonical alias path with an explicit repository URL and no supplied token variables; retrying through `--repository testpypi` correctly used the documented persisted configuration

Publication evidence captured in this session:

- TestPyPI upload command shape: `python -m twine upload --non-interactive --repository testpypi dist/calamum_test-0.3.0*`
- TestPyPI result: success
- TestPyPI URL: `https://test.pypi.org/project/calamum-test/0.3.0/`
- TestPyPI clean-install smoke: success in a fresh virtual environment using `--index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple`
- TestPyPI smoke outputs:
  - `calamum.__version__` -> `0.3.0`
  - `callable(calamum.api.list_definitions)` -> `True`
  - `calamum --version` -> `calamum 0.3.0`
- Production upload command shape: `python -m twine upload --non-interactive dist/calamum_test-0.3.0*`
- Production result: success
- Production URL: `https://pypi.org/project/calamum-test/0.3.0/`
- Production JSON API confirmed version `0.3.0` and both published artifacts
- Production simple-index propagation initially lagged behind the upload endpoint, then caught up during this session (`pip index versions calamum-test` reported `0.3.0` as latest)
- Production clean-install smoke: success in a fresh virtual environment from live PyPI
- Production smoke outputs:
  - `calamum.__version__` -> `0.3.0`
  - `callable(calamum.api.list_definitions)` -> `True`
  - `calamum --version` -> `calamum 0.3.0`
- Artifact hashes:
  - `calamum_test-0.3.0-py3-none-any.whl` -> `7c0a422f8e49336845761a98c5a865879dd7fbf5d328f81013467a873c118b6b`
  - `calamum_test-0.3.0.tar.gz` -> `429e2ff91e7d12da9eaa8872d2465413d172ea13c485455fe636b47cc5436b89`

- [x] Publish to TestPyPI first
- [x] Install from TestPyPI into a clean environment and smoke test
- [x] Publish to PyPI
- [x] Install from PyPI into a clean environment and smoke test
- [x] Record artifact hashes, install evidence, and final publish evidence

### M. Final release packet

- [x] Record final shipped version: `0.3.0`
- [x] Record install/runtime identity split explicitly
- [x] Record exact commands used for validation and publication
- [x] Record where fresh release evidence lives
- [x] Record any remaining bounded limitations honestly

Fresh release evidence for this publication lane lives in:

- this active remediation document
- local build artifacts under `projects/calamum/dist/`
- TestPyPI release page: `https://test.pypi.org/project/calamum-test/0.3.0/`
- production PyPI release page: `https://pypi.org/project/calamum-test/0.3.0/`
- production JSON API: `https://pypi.org/pypi/calamum-test/0.3.0/json`

Bounded limitation honestly recorded:

- the production simple index did not expose `0.3.0` immediately after upload; propagation completed during this session and the normal `pip install calamum-test==0.3.0` path then succeeded

## Post-publication full test continuation and aggregate evidence

Following publication and clean-install validation, the remaining compulsory follow-up actions were executed so the release lane ended with both retained-run evidence and full local suite evidence.

### 1. Full existing Calamum catalog executed through native `calamum test`

Live catalog discovery confirmed that the current shipped catalog contains exactly two definitions:

- `seed-cli-smoke`
- `seed-adversarial-smoke`

Because `calamum test run` currently accepts one explicit `definition_id` per invocation rather than a wildcard batch target, the full existing catalog was executed by enumerating the live definition list and running each definition through the native standalone surface.

Job id used for the full-suite batch:

- `full-existing-suite-20260502`

Retained run ids produced:

- `20260502T231251Z-seed-cli-smoke`
- `20260502T231253Z-seed-adversarial-smoke`

Per-run authoritative review via `calamum test runs show <run_id> --json` confirmed:

- decision: `go`
- result: `pass`
- all three canonical lanes passed for both definitions:
  - `pytest`
  - `sandbox_test`
  - `empirical_test`

Retained evidence roots:

- `projects/calamum/.calamum/generated/runs/20260502T231251Z-seed-cli-smoke/`
- `projects/calamum/.calamum/generated/runs/20260502T231253Z-seed-adversarial-smoke/`

Each retained run wrote the expected evidence pack:

- `report.json`
- `report.md`
- `manifest.json`
- `checksums.json`
- checksum sidecars
- per-lane stdout/stderr captures under:
  - `pytest/`
  - `sandbox_test/`
  - `empirical_test/`

### 2. Aggregate report generated for the full-suite job

The compulsory aggregate follow-up was then executed through the native reports surface:

- `calamum test reports generate --scope job --job full-existing-suite-20260502 --runs-root .calamum/generated/runs --reports-root .calamum/generated/reports --json`

Aggregate result:

- decision: `go`
- scope: `job`
- target: `full-existing-suite-20260502`
- report ref: `job:full-existing-suite-20260502`
- run count: `2`

Aggregate totals recorded:

- result totals:
  - `pass: 2`
- definition totals:
  - `seed-cli-smoke: 1`
  - `seed-adversarial-smoke: 1`
- lane totals:
  - `pytest: pass 2`
  - `sandbox_test: pass 2`
  - `empirical_test: pass 2`

Aggregate retained artifacts:

- `projects/calamum/.calamum/generated/reports/generated/job/full-existing-suite-20260502/report.json`
- `projects/calamum/.calamum/generated/reports/generated/job/full-existing-suite-20260502/report.md`
- `projects/calamum/.calamum/generated/reports/generated/job/full-existing-suite-20260502/manifest.json`
- `projects/calamum/.calamum/generated/reports/generated/job/full-existing-suite-20260502/receipt.json`
- history snapshot root:
  - `projects/calamum/.calamum/generated/reports/generated/job/full-existing-suite-20260502/history/20260502T231926Z`

This aggregate was also indexed in:

- `projects/calamum/.calamum/generated/reports/generated/report_index.jsonl`

### 3. Full local Calamum pytest suite executed after publication

Full local test command executed from `projects/calamum/`:

- `python -m pytest -q`

Observed result:

- `79 passed in 41.39s`

Assessment:

- no failures were found in the Calamum local pytest suite
- no remediation mutation was required after the post-publication continuation pass
- the release lane now has both:
  - native retained-run evidence for the existing Calamum catalog, and
  - full local regression-suite evidence from `pytest`

### 4. Final continuation conclusion

The originally suggested "handy follow up" actions should indeed have been treated as compulsory closeout steps for this release lane. They are now complete.

Final post-publication verification status:

- full existing native Calamum catalog: passed
- aggregate job report generation: passed
- full local Calamum pytest suite: passed
- remediation required after continuation pass: none

## Calamum tracked document/configuration audit

### TL;DR

Operator correction applied: `projects/calamum/jobs/` should **not** be tracked in the standalone Calamum repo. With that correction, the Calamum tracked document/configuration posture is only partially coherent: the subtree does cleanly separate tracked source/config surfaces from local-only generated evidence via `.gitignore`, and the tracked project descriptor points runtime outputs into `.calamum/generated/` as intended, **but** the currently tracked `jobs/` subtree is configuration drift relative to the intended Calamum-repo boundary. Additional drift remains where several release-facing files now exist on disk but are **not yet tracked**, most notably `CHANGELOG.md`, `MANIFEST.in`, and the `tools/` release-audit surface.

### Audit scope and validation basis

Audit basis used in this pass:

- tracked-surface inventory from `git ls-files projects/calamum`
- focused Calamum git-state readback from `git status --short -- projects/calamum`
- tracked local/runtime rules from:
  - `projects/calamum/.gitignore`
  - `projects/calamum/.calamum/generated/.gitignore`
  - `projects/calamum/.calamum/project.json`
- publish-facing inclusion rules from:
  - `projects/calamum/MANIFEST.in`
  - `projects/calamum/pyproject.toml`

Validation rubric used below:

- `PASS` = tracked and aligned with the current Calamum source/runtime contract
- `WARN` = tracked but intentionally supporting/non-authority, or present configuration drift needs operator awareness
- `INFO` = tracked guard/config surface whose purpose is containment rather than user-facing publication

### Width-safe tracked surface table

This table intentionally uses HTML rather than a pipe table so long relative paths do not over-widen markdown columns in VS Code preview or GitHub rendering. Paths use `<wbr>` soft-break points to keep wrapping stable. This table now lists only the surfaces that are appropriate as tracked Calamum-repo document/configuration surfaces under the corrected boundary.

<table>
  <thead>
    <tr>
      <th>ID</th>
      <th>Tracked surface</th>
      <th>Class</th>
      <th>State</th>
      <th>Rule / exposure</th>
      <th>Validation</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>T01</td>
      <td><code>projects/<wbr>calamum/<wbr>.gitignore</code></td>
      <td>git policy</td>
      <td>tracked</td>
      <td>ignores local outputs: <code>runs/</code>, <code>reports/</code>, <code>planning/</code>, <code>.calamum/generated/*</code>, logs, env</td>
      <td>PASS - tracked root ignore contract is explicit and matches local-only posture</td>
    </tr>
    <tr>
      <td>T02</td>
      <td><code>projects/<wbr>calamum/<wbr>.calamum/<wbr>generated/<wbr>.gitignore</code></td>
      <td>local guard</td>
      <td>tracked</td>
      <td>keeps generated runtime artifacts untracked while preserving the directory anchor</td>
      <td>INFO - correct containment guard for local generated output</td>
    </tr>
    <tr>
      <td>T03</td>
      <td><code>projects/<wbr>calamum/<wbr>.calamum/<wbr>project.json</code></td>
      <td>project descriptor</td>
      <td>tracked</td>
      <td>tracked source config; routes runs/reports to <code>.calamum/generated/...</code></td>
      <td>PASS - runtime roots and required paths align with current child-repo layout</td>
    </tr>
    <tr>
      <td>T04</td>
      <td><code>projects/<wbr>calamum/<wbr>pyproject.toml</code></td>
      <td>packaging config</td>
      <td>tracked, modified</td>
      <td>canonical package/build metadata; publish-facing</td>
      <td>PASS - tracked and authoritative for packaging; current working-tree edits are expected in this release lane</td>
    </tr>
    <tr>
      <td>T05</td>
      <td><code>projects/<wbr>calamum/<wbr>README.md</code></td>
      <td>public doc</td>
      <td>tracked, modified</td>
      <td><code>readme</code> source in <code>pyproject.toml</code>; included in sdist</td>
      <td>PASS - canonical public entry doc is tracked and publish-addressable</td>
    </tr>
    <tr>
      <td>T06</td>
      <td><code>projects/<wbr>calamum/<wbr>CONTRIBUTING.md</code></td>
      <td>contributor doc</td>
      <td>tracked, modified</td>
      <td>included in sdist by <code>MANIFEST.in</code></td>
      <td>PASS - tracked contributor guidance with current release-lane edits</td>
    </tr>
    <tr>
      <td>T07</td>
      <td><code>projects/<wbr>calamum/<wbr>SECURITY.md</code></td>
      <td>security doc</td>
      <td>tracked</td>
      <td>included in sdist by <code>MANIFEST.in</code></td>
      <td>PASS - tracked security posture doc aligned to retained-evidence model</td>
    </tr>
    <tr>
      <td>T08</td>
      <td><code>projects/<wbr>calamum/<wbr>catalog/<wbr>test_definitions.json</code></td>
      <td>tracked catalog</td>
      <td>tracked</td>
      <td>authoritative test-library input; local runtime consumes it directly</td>
      <td>PASS - tracked catalog contract is explicit and populated</td>
    </tr>
  </tbody>
</table>

### Observed tracked-drift surfaces under `projects/calamum/jobs/`

The following paths were observed as tracked in the current monorepo workspace, but under the corrected Calamum-repo boundary they should be treated as **tracking drift**, not desired steady-state tracked surfaces for the standalone Calamum repo.

<table>
  <thead>
    <tr>
      <th>ID</th>
      <th>Observed tracked path</th>
      <th>Class</th>
      <th>Correct repo posture</th>
      <th>Validation</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>J01</td>
      <td><code>projects/<wbr>calamum/<wbr>jobs/<wbr>JOB_0001_CALAMUM_IMPLEMENTATION_TOOLS-GATE-LIFECYCLE_20260502/<wbr>JOB.json</code></td>
      <td>job spine</td>
      <td>should not be tracked in standalone Calamum repo</td>
      <td>WARN - currently tracked here, but belongs outside Calamum-repo tracked scope</td>
    </tr>
    <tr>
      <td>J02</td>
      <td><code>projects/<wbr>calamum/<wbr>jobs/<wbr>JOB_0001_CALAMUM_IMPLEMENTATION_TOOLS-GATE-LIFECYCLE_20260502/<wbr>JOB.md</code></td>
      <td>job spine</td>
      <td>should not be tracked in standalone Calamum repo</td>
      <td>WARN - currently tracked here, but belongs outside Calamum-repo tracked scope</td>
    </tr>
    <tr>
      <td>J03</td>
      <td><code>projects/<wbr>calamum/<wbr>jobs/<wbr>JOB_0001_CALAMUM_IMPLEMENTATION_TOOLS-GATE-LIFECYCLE_20260502/<wbr>QS.json</code></td>
      <td>queststack</td>
      <td>should not be tracked in standalone Calamum repo</td>
      <td>WARN - lifecycle stack artifact is out of Calamum-repo tracked scope</td>
    </tr>
    <tr>
      <td>J04</td>
      <td><code>projects/<wbr>calamum/<wbr>jobs/<wbr>JOB_0001_CALAMUM_IMPLEMENTATION_TOOLS-GATE-LIFECYCLE_20260502/<wbr>QF.md</code></td>
      <td>questframe</td>
      <td>should not be tracked in standalone Calamum repo</td>
      <td>WARN - frame artifact is out of Calamum-repo tracked scope</td>
    </tr>
    <tr>
      <td>J05</td>
      <td><code>projects/<wbr>calamum/<wbr>jobs/<wbr>JOB_0001_CALAMUM_IMPLEMENTATION_TOOLS-GATE-LIFECYCLE_20260502/<wbr>MANIFEST.json</code></td>
      <td>job manifest</td>
      <td>should not be tracked in standalone Calamum repo</td>
      <td>WARN - closeout inventory is useful in this monorepo lane but should not live in tracked Calamum-repo state</td>
    </tr>
    <tr>
      <td>J06</td>
      <td><code>projects/<wbr>calamum/<wbr>jobs/<wbr>JOB_0001_CALAMUM_IMPLEMENTATION_TOOLS-GATE-LIFECYCLE_20260502/<wbr>JOB.md.resolution_trace.json</code></td>
      <td>trace artifact</td>
      <td>should not be tracked in standalone Calamum repo</td>
      <td>WARN - supporting trace artifact is outside intended tracked repo boundary</td>
    </tr>
    <tr>
      <td>J07</td>
      <td><code>projects/<wbr>calamum/<wbr>jobs/<wbr>JOB_0001_CALAMUM_IMPLEMENTATION_TOOLS-GATE-LIFECYCLE_20260502/<wbr>CALAMUM_HELP_SURFACE_REPACKAGING_INVESTIGATION_AND_REMEDIATION_20260502.md</code></td>
      <td>supporting investigation</td>
      <td>should not be tracked in standalone Calamum repo</td>
      <td>WARN - current execution surface exists here for this CodeSentinel monorepo lane, but is not valid steady-state tracked Calamum-repo content</td>
    </tr>
    <tr>
      <td>J08</td>
      <td><code>projects/<wbr>calamum/<wbr>jobs/<wbr>JOB_0001_CALAMUM_IMPLEMENTATION_TOOLS-GATE-LIFECYCLE_20260502/<wbr>CALAMUM_JOB_PIPELINE_SSOT_AUDIT_SCRATCHPAD_20260502.md</code></td>
      <td>scratchpad</td>
      <td>should not be tracked in standalone Calamum repo</td>
      <td>WARN - supporting scratchpad is outside intended tracked repo boundary</td>
    </tr>
    <tr>
      <td>J09</td>
      <td><code>projects/<wbr>calamum/<wbr>jobs/<wbr>JOB_0001_CALAMUM_IMPLEMENTATION_TOOLS-GATE-LIFECYCLE_20260502/<wbr>CALAMUM_MONITOR_EVIDENCE_ARCHITECTURE_PROPOSAL_20260501.md</code></td>
      <td>proposal</td>
      <td>should not be tracked in standalone Calamum repo</td>
      <td>WARN - proposal artifact is outside intended tracked repo boundary</td>
    </tr>
    <tr>
      <td>J10</td>
      <td><code>projects/<wbr>calamum/<wbr>jobs/<wbr>JOB_0001_CALAMUM_IMPLEMENTATION_TOOLS-GATE-LIFECYCLE_20260502/<wbr>CALAMUM_MONITOR_EVIDENCE_ARCHITECTURE_SCRATCHPAD_20260501.md</code></td>
      <td>scratchpad</td>
      <td>should not be tracked in standalone Calamum repo</td>
      <td>WARN - scratchpad artifact is outside intended tracked repo boundary</td>
    </tr>
  </tbody>
</table>

### Current drift findings

Present on disk but **not currently tracked** in git:

- `projects/calamum/CHANGELOG.md`
- `projects/calamum/MANIFEST.in`
- `projects/calamum/tools/` (including the release-audit script introduced in this lane)

Additionally, the following directory is currently observed as **tracked but should not be tracked** under the corrected Calamum-repo posture:

- `projects/calamum/jobs/`

And these untracked files currently sit under that same out-of-boundary subtree:

- `projects/calamum/jobs/JOB_0001_CALAMUM_IMPLEMENTATION_TOOLS-GATE-LIFECYCLE_20260502/release_version_audit_0_3_0.json`
- `projects/calamum/jobs/JOB_0001_CALAMUM_IMPLEMENTATION_TOOLS-GATE-LIFECYCLE_20260502/release_version_audit_0_3_0.md`

Assessment of the drift:

- `CHANGELOG.md` is release-facing documentation and should be tracked if it is intended to remain part of the public Calamum contract.
- `MANIFEST.in` is packaging configuration and should be tracked if the repo intends reproducible source-distribution inclusion rules.
- the currently tracked `projects/calamum/jobs/` subtree is drift relative to the intended standalone Calamum-repo boundary and should be treated as out-of-scope tracked content for that repo.
- the `release_version_audit_0_3_0.*` files are evidence artifacts inside a subtree that the operator has clarified should not be tracked in the Calamum repo.
- the untracked `tools/` subtree is a governance gap if Calamum intends the release-audit script to remain part of the maintained tool surface.

### Configuration findings by layer

#### Git tracking / ignore posture

- root `projects/calamum/.gitignore` correctly excludes local-only outputs (`runs/`, `reports/`, `planning/`, env, logs, generated runtime output)
- tracked `.calamum/generated/.gitignore` correctly preserves the local output root while keeping generated contents untracked
- this layout is coherent and supports the local-first retained-evidence model

#### Runtime/project configuration posture

- tracked `.calamum/project.json` is internally consistent with the child-repo layout:
  - catalog root -> `catalog`
  - runs root -> `.calamum/generated/runs`
  - reports root -> `.calamum/generated/reports`
  - required markers / paths -> `pyproject.toml`, `src`, `tests`, `catalog`
- no obvious descriptor drift was found in this pass

#### Packaging/publication posture

- `pyproject.toml` is tracked and remains the authoritative packaging configuration
- `README.md` is the declared project readme and is tracked
- `MANIFEST.in` currently includes `README.md`, `CHANGELOG.md`, `CONTRIBUTING.md`, `SECURITY.md`, and branding assets
- because `MANIFEST.in` and `CHANGELOG.md` are currently untracked, the source-distribution policy is working from live working-tree state rather than fully governed repo state

#### Job-paperwork posture

- operator correction: `projects/calamum/jobs/` should not be tracked in the standalone Calamum repo
- accordingly, the currently tracked Calamum job root is not a sign of healthy steady-state Calamum-repo configuration; it is tracked-boundary drift in the current monorepo workspace
- the supporting paperwork may still be useful to this CodeSentinel execution lane, but it should not be counted as valid tracked document/configuration state for the standalone Calamum repo

### Recommendation packet

Recommended next actions for the Calamum subtree configuration:

1. track `projects/calamum/MANIFEST.in` if the current sdist inclusion rules are intended to remain canonical
2. track `projects/calamum/CHANGELOG.md` if release-history visibility is intended to remain part of the public package surface
3. remove or relocate `projects/calamum/jobs/` from the standalone Calamum repo tracking boundary; it should not remain tracked there
4. treat the `release_version_audit_0_3_0.*` outputs as out-of-boundary evidence artifacts while they live under `projects/calamum/jobs/`
5. decide whether `projects/calamum/tools/release_version_audit.py` is a durable maintained tool or a one-off lane artifact; track or archive accordingly
6. keep the current `.gitignore` plus `.calamum/generated/.gitignore` split; it is doing the right thing

### Checklist to update the standalone Calamum tracked schema

Use this as the concrete migration checklist for the public `joediggidyyy/calamum` repository surface.

- [ ] Treat `projects/calamum/jobs/` as out-of-boundary content for the standalone Calamum repo
- [ ] Add `jobs/` to the standalone Calamum ignore policy so accidental local job artifacts do not enter repo tracking
- [ ] Keep these runtime/config anchors tracked:
  - [ ] `.calamum/project.json`
  - [ ] `.calamum/generated/.gitignore`
  - [ ] `.env.example`
  - [ ] `.gitignore`
- [ ] Keep these public/package docs tracked:
  - [ ] `README.md`
  - [ ] `CONTRIBUTING.md`
  - [ ] `SECURITY.md`
  - [ ] `LICENSE`
  - [ ] `CHANGELOG.md`
- [ ] Keep these packaging/config surfaces tracked:
  - [ ] `pyproject.toml`
  - [ ] `MANIFEST.in`
- [ ] Keep these product/runtime surfaces tracked:
  - [ ] `assets/branding/**`
  - [ ] `catalog/test_definitions.json`
  - [ ] `src/calamum/**`
  - [ ] `tests/**`
  - [ ] `tools/release_version_audit.py`
- [ ] Keep these local-only surfaces out of standalone tracking:
  - [ ] `jobs/`
  - [ ] `planning/`
  - [ ] `runs/`
  - [ ] `reports/`
  - [ ] `dist/`
  - [ ] `build/`
  - [ ] `logs/`
  - [ ] `.agent_session/`
  - [ ] `.calamum/generated/**` except the tracked `.gitignore` anchor
  - [ ] `.env`
  - [ ] `codesentinel.log`
- [ ] Validate the standalone repo working tree after sync to confirm only intended tracked surfaces remain
- [ ] Run standalone repo validation:
  - [ ] editable/install validation in a clean environment
  - [ ] `pytest`
  - [ ] `python -m build`
  - [ ] `twine check`
  - [ ] `calamum --version`
- [ ] Push the validated standalone tree to the public `joediggidyyy/calamum` repository

### Standalone repo validation and public push outcome

Execution outcome for the standalone public-repo lane:

- public repo URL confirmed: `https://github.com/joediggidyyy/calamum`
- standalone validation clone path: `%TEMP%/calamum-public-audit`
- corrected standalone tracking boundary applied during sync:
  - `jobs/` excluded from the synced public tree
  - `jobs/` added to `.gitignore`
  - release-facing additions included in the public tree:
    - `CHANGELOG.md`
    - `MANIFEST.in`
    - `tools/release_version_audit.py`
    - `tests/test_runner.py`

Validation results in the standalone clone:

- `pytest -q` -> `79 passed in 43.36s`
- `python -m build` -> passed
- `python -m twine check dist/*` -> passed
- `calamum --version` -> `calamum 0.3.0`

Public push result:

- target repo: `joediggidyyy/calamum`
- target branch: `main`
- pushed commit: `33f7b4b`
- commit message: `Sync standalone schema and 0.3.0 release surfaces`

Checklist closeout status:

- standalone tracked-schema checklist: generated
- standalone repo validation: passed
- public push: passed

### Table-formatting guidance for path-heavy audits

To avoid malformed tables when long file paths are involved, use one of these configurations:

1. **Preferred for mixed renderers**: HTML table + `<code>` + `<wbr>` soft breaks
   - works better than pipe tables for long paths
   - keeps columns from being forced open by one long token

2. **Best for very large inventories**: short ID table + path legend below
   - keep the table columns narrow
   - move the full path text into a numbered list or appendix

3. **Best for VS Code Preview only**: workspace markdown-preview CSS
   - this repo already has a known workspace solution for VS Code preview wrapping using fixed-layout tables and aggressive wrap rules
   - that helps VS Code preview specifically, but it does **not** control GitHub/web rendering

4. **Most portable fallback**: replace the table with a definition list or bullet inventory when path length dominates the content
   - if the path is more important than side-by-side comparison, a non-table layout is often the most robust option

For this audit, the HTML-table approach is the safest default because it preserves side-by-side validation while avoiding the common long-path column blowout.
