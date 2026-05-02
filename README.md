# Calamum Test

<p align="center">
	<img src="https://raw.githubusercontent.com/joediggidyyy/calamum/main/assets/branding/calamum_logo_color.png" alt="Calamum logo" width="360">
</p>

`Calamum Test` is a standalone, project-aware testing substrate for consolidating `pytest`, `sandbox_test`, and `empirical_test` lanes behind one retained-evidence CLI and Python facade.

Public repository: `https://github.com/joediggidyyy/calamum`

## Install and verify

Install from PyPI using the published distribution name:

- `pip install calamum-test`

Run the installed CLI using the runtime command name:

- `calamum --version`
- `calamum -h`

Important naming note:

- PyPI package / dependency name: `calamum-test`
- import package and runtime command: `calamum`

The current implementation is no longer just a seed scaffold. It now includes:

- a shared `.calamum/project.json` descriptor model
- machine-local overlay and active-project state support
- a stable importable Python facade in `calamum.api`
- richer catalog metadata for profiles, tags, policy flags, and evidence requirements
- retained run manifests and checksums
- regenerative aggregate reports for `job`, `project`, and `domain` scopes
- detached-signature support for privileged or publishable aggregate artifacts

## Command surface

### Top-level families

- `calamum test` — validation definition discovery and execution
- `calamum project` — project registration, active-project state, and context readback
- `calamum monitor` — current monitor-shell scaffolding and capability readback

### Test execution

- `calamum test list`
- `calamum test show <definition_id>`
- `calamum test run <definition_id>`
- `calamum test runs list`
- `calamum test runs show <run_id>`

A `definition_id` is the exact id of a test definition in the catalog. Use
`calamum test list` to discover the available ids, then pass one of those ids to
`calamum test show` or `calamum test run`. Example: `seed-cli-smoke`.

**Progress visibility**: `calamum test run` emits a heartbeat line to stderr every
20 seconds while a long-running step subprocess is active. This indicates the
orchestrator is alive and the step is progressing, not stalled. The retained-evidence
artifacts (`report.json`, `report.md`, `manifest.json`, `checksums.json`) are
written only after the step completes; heartbeat lines are transient and not stored.

### Project management

- `calamum project register`
- `calamum project set <project>`
- `calamum project current`
- `calamum project validate [<project>]`
- `calamum project list`
- `calamum project show <project>`

Compatibility note:

- `calamum test project ...` remains available as a compatibility alias during the current route migration.

### Monitor scaffolding

- `calamum monitor capability list`

Current note:

- the top-level `monitor` family is now present as native Calamum scaffolding for future monitor adapters and readiness surfaces;
- broader monitor execution families are still a follow-on implementation lane, so current help/runtime output should be treated as the truthful monitor-shell baseline rather than a claim of full capture parity.

### Aggregate reporting

- `calamum test reports list`
- `calamum test reports show <report_ref>`
- `calamum test reports generate --scope job --job <job_id>`
- `calamum test reports generate --scope project [--project <project>]`
- `calamum test reports generate --scope domain --domain <domain>`

## Adding tests to the library

In Calamum, the public "test library" is the tracked catalog at
`catalog/test_definitions.json`.

Current authoring workflow:

1. add a new definition object to the catalog `definitions` list
2. give it a stable `id`, `title`, `summary`, `status`, and `category`
3. classify it with:
	- `category` — primary test class (for example `bootstrap`, `regression`, `security`, `adversarial`, `performance`)
	- `profiles` — reusable bundles such as `smoke`, `release`, or `nightly`
	- `tags` — cross-cutting labels for search and future selectors
	- `policy_flags` — execution or governance rules
	- `evidence_requirements` — retained outputs the definition must produce
4. declare step arrays under the canonical lanes:
	- `pytest`
	- `sandbox_test`
	- `empirical_test`
5. validate the new entry by running:
	- `calamum test list`
	- `calamum test show <definition_id>`
	- `calamum test run <definition_id> --dry-run`

Minimal definition shape:

```json
{
	"id": "adversarial-auth-smoke",
	"title": "Adversarial auth smoke",
	"summary": "Challenge the authentication path with hostile-input and retained-evidence checks.",
  "status": "active",
	"category": "adversarial",
  "profiles": ["smoke", "release"],
	"tags": ["adversarial", "auth", "api", "signing"],
	"policy_flags": ["containment", "json-first", "project-aware", "release-gate"],
	"evidence_requirements": ["report_json", "report_md", "manifest_json", "checksums_json"],
  "default_lanes": ["pytest", "sandbox_test"],
  "lanes": {
	 "pytest": [],
	 "sandbox_test": [],
	 "empirical_test": []
  }
}
```

Current limitation: authoring is still manual. Calamum does **not** yet ship a
dedicated `calamum test catalog scaffold|validate` management surface, so the
catalog file remains the authoritative place to add new tests today.

### Plain-language meaning of the fields

- `category` = **what kind of test this is**
- `profiles` = **when or why you run it**
- `tags` = **what area it touches**
- `policy_flags` = **special execution or governance rules**
- `evidence_requirements` = **which retained outputs must exist after the run**
- `pytest` / `sandbox_test` / `empirical_test` = **the three execution lane classes inside one definition**

The important division is this:

- one **definition** = one named test in the library
- one definition can use **one, two, or all three lane classes**
- the lane classes are **not** separate library entries; they are the three ways Calamum can gather evidence for the same test

## Controlled library vocabulary (v1)

Calamum now treats the following values as the contracted v1 vocabulary.

### Status values

- `seed` — scaffold or early placeholder definition
- `active` — supported definition for normal use
- `experimental` — usable but still being evaluated
- `deprecated` — still readable/runnable for transition purposes but being retired
- `disabled` — present in the catalog but not intended for ordinary execution

### Category values

- `adversarial` — deliberate hostile-input, penetration-style, abuse-case, or attack-path validation
- `general` — mixed or uncategorized definition; use sparingly
- `bootstrap` — proves basic setup, installation, or command-surface readiness
- `regression` — protects a known workflow or behavior from breaking
- `security` — validates defensive trust, signing, access, or safety posture without making hostile challenge the primary identity
- `performance` — validates speed, scale, or resource posture
- `integration` — validates interaction across modules, services, or host applications
- `compliance` — validates policy, contract, or governance conformance

### Profile values

- `default` — ordinary day-to-day execution set
- `smoke` — fast confidence check
- `fast` — low-cost local developer check
- `release` — required before publishing or promotion
- `nightly` — broader scheduled validation pack

### Tag values

- `adversarial` — hostile-input / penetration-testing facet on a definition whose primary category may or may not already be adversarial
- `aggregate` — aggregate/report generation surface
- `api` — Python or service API surface
- `auth` — authentication / authorization surface
- `catalog` — definition-library / schema surface
- `cli` — command-line surface
- `filesystem` — path, layout, or artifact-root surface
- `project` — project registration / context resolution surface
- `reporting` — rendered reports or report-regeneration surface
- `retained-evidence` — manifests, checksums, receipts, or persisted review evidence
- `sandbox` — isolated or simulated runtime surface
- `signing` — signatures, receipts, or verification surface
- `smoke` — broad confidence check spanning multiple surfaces

### Policy flag values

- `json-first` — JSON is the primary machine contract
- `project-aware` — requires resolved project context or tokens
- `containment` — paths and execution roots must stay inside declared boundaries
- `local-only` — intentionally local-only workflow or artifact posture
- `signed-output` — output must be signed and verifiable
- `privileged-operation` — delegated or privileged control path
- `release-gate` — failing result blocks release or promotion
- `deterministic-output` — output is expected to be stable and reproducible

### Evidence requirement values

- `report_json`
- `report_md`
- `manifest_json`
- `checksums_json`
- `stdout_capture`
- `stderr_capture`
- `receipt_json`
- `report_signature`
- `manifest_signature`

### Lane classes

- `pytest` — automated code-level assertions
- `sandbox_test` — controlled scripted or simulated execution
- `empirical_test` — real observed/manual/live verification

### How adversarial testing is represented

- use `category: adversarial` when hostile challenge or penetration-style probing is the **primary identity** of the definition
- use tag `adversarial` when a definition is primarily something else (for example `security` or `regression`) but still contains adversarial coverage
- keep `adversarial` out of the lane field: it is a **test type**, not an execution medium
- execute adversarial definitions through one or more of the normal lanes (`pytest`, `sandbox_test`, `empirical_test`)
- when adversarial coverage is claimed, sandbox coverage should normally be present because that is the safest place to exercise hostile-path probes first

## Plain-language workflow across all three test classes

Here is the simplest way to think about it.

Use **one definition** when you are testing **one real thing**.

Example definition:

- id: `adversarial-auth-smoke`
- category: `adversarial`
- profiles: `smoke`, `release`
- tags: `adversarial`, `auth`, `api`, `signing`

Then split the same test across the three lane classes like this:

1. **`pytest` lane**
	- prove the code-level rules work
	- example: token validation, permission checks, malformed-input rejection, JSON packet shape
2. **`sandbox_test` lane**
	- prove the command or workflow works in a controlled runtime
	- example: run the CLI against hostile fixtures in a safe local sandbox and confirm the right files are written without escaping containment
3. **`empirical_test` lane**
	- prove the result also holds in a real observed workflow
	- example: operator checks the real auth flow or a live delegated request/receipt path under adversarial review conditions

Plain English summary:

- `pytest` asks: **does the code logic pass?**
- `sandbox_test` asks: **does the workflow run correctly in a safe controlled environment?**
- `empirical_test` asks: **does it still look correct when a human or real-world run observes it?**

Typical full workflow:

1. add the definition to `catalog/test_definitions.json`
2. run `calamum test show adversarial-auth-smoke`
3. run `calamum test run adversarial-auth-smoke --dry-run`
4. run `calamum test run adversarial-auth-smoke`
5. inspect one combined retained evidence pack under:
	- `.calamum/generated/runs/<run_id>/`
6. if the run belongs to a job or release lane, generate aggregates under:
	- `.calamum/generated/reports/generated/`

That is the core model: **one named adversarial or non-adversarial test definition, three possible lane classes, one retained evidence pack.**

## Retained evidence contract

Every `calamum test run` retains:

- `report.json`
- `report.md`
- `checksums.json`
- `manifest.json`
- per-step stdout/stderr captures
- append-only `.calamum/generated/runs/run_index.jsonl`

Aggregate report generation retains:

- `report.json`
- `report.md`
- `manifest.json`
- `receipt.json`
- checksum sidecars
- optional detached signatures for JSON artifacts

## Filesystem layout and default output contract

Calamum uses a small split between tracked inputs and local-only generated outputs.

Tracked by default:

- `.calamum/project.json` — shared project descriptor
- `catalog/test_definitions.json` — tracked definition catalog

Local-only by default:

- `.calamum/generated/runs/` — retained run evidence
- `.calamum/generated/reports/` — materialized aggregate reports
- `.calamum/generated/.gitignore` — local-only guard so generated output stays untracked

Default tree:

```text
project-root/
├─ .calamum/
│  ├─ project.json
│  └─ generated/
│     ├─ .gitignore
│     ├─ runs/
│     │  ├─ run_index.jsonl
│     │  └─ <run_id>/
│     │     ├─ report.json
│     │     ├─ report.md
│     │     ├─ checksums.json
│     │     ├─ manifest.json
│     │     └─ <lane>/
│     │        ├─ <step>.stdout.txt
│     │        └─ <step>.stderr.txt
│     └─ reports/
│        └─ generated/
│           ├─ report_index.jsonl
│           └─ <scope>/
│              └─ <target>/
│                 ├─ report.json
│                 ├─ report.md
│                 ├─ manifest.json
│                 ├─ receipt.json
│                 ├─ *.sha256
│                 ├─ *.sig                # when signing is enabled
│                 └─ history/<timestamp>/
└─ catalog/
	 └─ test_definitions.json
```

This is the default contract unless the operator overrides one or more roots during
project registration or later through local overlay settings / explicit CLI flags.

### Workflow notes

- **Child-repo / self-hosted workflow**: the checked-in `projects/calamum/.calamum/project.json`
	points generated outputs into `.calamum/generated/`.
- **Adopt an existing repo**: `calamum test project register` now bootstraps the minimal
	local scaffold by creating:
	- `catalog/test_definitions.json` if it does not exist yet
	- `.calamum/generated/.gitignore`
	- the standard `runs/` and `reports/` directories under `.calamum/generated/`
- **Application profile note**: `--application <id>` is currently stored on the project record and exposed to tokens/readback,
	but it does **not yet** auto-expand a data-driven profile with implied markers, path aliases, or report defaults.
	For CodeSentinel, pass the explicit registration arguments you want on the first local exercise.
- **Override workflow**: `--runs-root`, `--reports-root`, `--catalog-root`, and the machine-local
	overlay still win when the operator intentionally wants a different layout.

If you do not override anything, test reports go to `.calamum/generated/runs/` and
aggregate reports go to `.calamum/generated/reports/generated/`.

Concrete local-first CodeSentinel workflow notes now live in:

- `planning/CALAMUM_CODESENTINEL_LOCAL_ADOPTION_SCRATCHPAD_20260423.md`

## Project resolution order

Calamum resolves project context in the following order:

1. explicit `--project`
2. nearest ancestor `.calamum/project.json`
3. `CALAMUM_PROJECT`
4. active project stored in local state

Within a resolved project, path/runtime resolution follows:

1. explicit command flags
2. machine-local overlay
3. shared descriptor
4. built-in defaults

## Quick start

From `projects/calamum/`:

1. install in editable mode
2. validate the default shared descriptor
3. run the seed smoke definition
4. generate a project aggregate from retained evidence

Example flow:

- `python -m pip install -e .[dev]`
- `calamum --version`
- `calamum project current --json`
- `calamum test list --json`
- `calamum test run seed-cli-smoke --job local-smoke --json`
- `calamum test reports generate --scope project --project calamum-test --json`

After the sample run, inspect:

- `.calamum/generated/runs/run_index.jsonl`
- `.calamum/generated/reports/generated/report_index.jsonl`

If you want to avoid installing the console script during early development, run `python -m calamum ...` from the project root after setting `PYTHONPATH=src` for the session.

## Signing and privileged flows

Privileged aggregate generation can verify detached requests and emit signed receipts and report artifacts.

Relevant local environment variables:

- `CALAMUM_ED25519_PRIVATE_KEY`
- `CALAMUM_ED25519_PUBLIC_KEY`
- `CALAMUM_POLICY_SIGNING_KEY`
- `CALAMUM_CONFIG_ROOT`

For local development, a fallback HMAC or SHA lane is supported. For publishable or cross-application flows, prefer Ed25519.

## Python facade

The package exports a stable surface for host applications via `calamum.api`, including helpers to:

- resolve or require project context
- register and validate projects
- list/show/run definitions
- list/show retained runs
- generate/list/show aggregate reports

## Why this repo exists

This child project adapts the strongest patterns from the earlier Calamum/observer testing surfaces into one reusable testing substrate with a cleaner release boundary.

The design goals are:

- deterministic project-aware execution
- retained evidence instead of terminal-history dependence
- JSON-first machine readability with Markdown companions
- regenerable report surfaces
- credible privileged/publication security hooks without hardcoding secrets
