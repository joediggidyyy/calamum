# Calamum Test

<p align="center">
	<img src="assets/branding/calamum_logo_color.png" alt="Calamum logo" width="360">
</p>

`Calamum Test` is a standalone, project-aware testing harness for consolidating `pytest`, `sandbox_test`, and `empirical_test` lanes behind one retained-evidence CLI and Python facade.

It is built for teams that want test execution, project context, and generated evidence to stay organized, reviewable, and reproducible.

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

Package highlights include:

- a shared `.calamum/project.json` descriptor model
- project-aware resolution for catalog, runs, and reports roots
- a stable Python facade in `calamum.api`
- tracked catalog metadata for profiles, tags, policy flags, and evidence requirements
- retained run manifests, checksums, and per-step output captures
- aggregate report generation for `job`, `project`, and `domain` scopes
- optional signing inputs for privileged or publication-oriented report flows

## Command surface

### Top-level families

- `calamum test` — validation definition discovery, execution, and retained evidence review
- `calamum project` — project registration, active-project state, and context readback
- `calamum monitor` — current monitor-shell scaffolding and capability readback

### Test execution

- `calamum test list`
- `calamum test show <definition_id>`
- `calamum test run <definition_id>`
- `calamum test runs list`
- `calamum test runs show <run_id>`

A `definition_id` is the exact id of a test definition in the catalog. Use `calamum test list` to discover available ids, then pass one of those ids to `calamum test show` or `calamum test run`.

The catalog currently includes definitions such as:

- `seed-cli-smoke`
- `seed-adversarial-smoke`

Long-running subprocess steps emit heartbeat lines to `stderr` while a run is active. Those heartbeats are transient status signals; the retained artifacts are written when the run completes.

### Project management

- `calamum project register`
- `calamum project set <project>`
- `calamum project current`
- `calamum project validate [<project>]`
- `calamum project list`
- `calamum project show <project>`

Compatibility note:

- `calamum test project ...` remains available as a compatibility alias for the top-level `project` family.

### Monitor scaffolding

- `calamum monitor capability list`

The `monitor` family currently provides capability inspection through `calamum monitor capability list`.

### Aggregate reporting

- `calamum test reports list`
- `calamum test reports show <report_ref>`
- `calamum test reports generate --scope job --job <job_id>`
- `calamum test reports generate --scope project [--project <project>]`
- `calamum test reports generate --scope domain --domain <domain>`

## Adding tests to the library

In Calamum, the public test library is the tracked catalog at `catalog/test_definitions.json`.

To add a definition:

1. add a new definition object to the catalog `definitions` list
2. give it a stable `id`, `title`, `summary`, `status`, and `category`
3. classify it with:
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

Definitions are currently added directly in `catalog/test_definitions.json`, which remains the authoritative editing surface.

### What the fields mean

- `category` = what kind of test this is
- `profiles` = when or why you run it
- `tags` = what area it touches
- `policy_flags` = special execution or governance rules
- `evidence_requirements` = which retained outputs must exist after the run
- `pytest` / `sandbox_test` / `empirical_test` = the three execution lane classes inside one definition

The important division is this:

- one definition = one named test in the library
- one definition can use one, two, or all three lane classes
- the lane classes are not separate library entries; they are the three ways Calamum gathers evidence for the same test

## Controlled library vocabulary (v1)

Calamum treats the following values as the contracted v1 vocabulary.

### Status values

- `seed` — scaffold or early placeholder definition
- `active` — supported definition for normal use
- `experimental` — usable but still being evaluated
- `deprecated` — still readable or runnable for transition purposes
- `disabled` — present in the catalog but not intended for ordinary execution

### Category values

- `adversarial` — hostile-input, penetration-style, or abuse-case validation
- `general` — mixed or uncategorized definition
- `bootstrap` — setup, installation, or command-surface readiness
- `regression` — protects a known workflow or behavior from breaking
- `security` — validates defensive trust, signing, access, or safety posture
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

- `adversarial`
- `aggregate`
- `api`
- `auth`
- `catalog`
- `cli`
- `filesystem`
- `project`
- `reporting`
- `retained-evidence`
- `sandbox`
- `signing`
- `smoke`

### Policy flag values

- `json-first`
- `project-aware`
- `containment`
- `local-only`
- `signed-output`
- `privileged-operation`
- `release-gate`
- `deterministic-output`

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
- `empirical_test` — real observed or manual verification

### How adversarial testing is represented

- use `category: adversarial` when hostile challenge is the primary identity of the definition
- use tag `adversarial` when a definition is primarily something else but still includes adversarial coverage
- keep `adversarial` out of the lane field; it is a test type, not an execution medium
- execute adversarial definitions through one or more of the normal lanes

## How the three test classes work together

The simplest mental model is: use one definition when you are testing one real thing.

Example definition:

- id: `adversarial-auth-smoke`
- category: `adversarial`
- profiles: `smoke`, `release`
- tags: `adversarial`, `auth`, `api`, `signing`

Then split the same test across the three lane classes like this:

1. `pytest` lane
   - proves the code-level rules work
   - example: token validation, permission checks, malformed-input rejection
2. `sandbox_test` lane
   - proves the workflow runs correctly in a controlled runtime
   - example: run the CLI against hostile fixtures in a safe local sandbox
3. `empirical_test` lane
   - proves the result still holds in a real observed workflow
   - example: operator review of a real auth flow or delegated request path

In short:

- `pytest` asks: does the code logic pass?
- `sandbox_test` asks: does the workflow run correctly in a safe controlled environment?
- `empirical_test` asks: does it still look correct when a human or real-world run observes it?

Typical full workflow:

1. add the definition to `catalog/test_definitions.json`
2. run `calamum test show adversarial-auth-smoke`
3. run `calamum test run adversarial-auth-smoke --dry-run`
4. run `calamum test run adversarial-auth-smoke`
5. inspect one combined retained evidence pack under `.calamum/generated/runs/<run_id>/`
6. if the run belongs to a job or release lane, generate aggregates under `.calamum/generated/reports/generated/`

That is the core model: one named test definition, up to three lane classes, and one retained evidence pack.

## Retained evidence contract

Every `calamum test run` retains:

- `report.json`
- `report.md`
- `checksums.json`
- `manifest.json`
- per-step stdout and stderr captures
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
│                 ├─ *.sig
│                 └─ history/<timestamp>/
└─ catalog/
	└─ test_definitions.json
```

### Notes

- the checked-in `.calamum/project.json` points outputs into `.calamum/generated/`
- `calamum project register` can bootstrap the minimal local scaffold for an adopted repo
- explicit command flags override descriptor defaults when you intentionally want a different layout

If you do not override anything, retained test runs go to `.calamum/generated/runs/` and aggregate reports go to `.calamum/generated/reports/generated/`.

## Project resolution order

Calamum resolves project context in the following order:

1. explicit `--project`
2. nearest ancestor `.calamum/project.json`
3. `CALAMUM_PROJECT`
4. active project stored in local state

Within a resolved project, path resolution follows:

1. explicit command flags
2. machine-local overlay
3. shared descriptor
4. built-in defaults

## Quick start

From `projects/calamum/`:

1. install in editable mode
2. validate the default shared descriptor
3. list the current seed definitions
4. run a seed smoke definition
5. generate a project aggregate from retained evidence

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

## Signing and privileged flows

Aggregate generation supports optional signing inputs for privileged or publication-oriented flows.

Relevant environment variables include:

- `CALAMUM_ED25519_PRIVATE_KEY`
- `CALAMUM_ED25519_PUBLIC_KEY`
- `CALAMUM_POLICY_SIGNING_KEY`
- `CALAMUM_CONFIG_ROOT`

The repository also includes `.env.example` with placeholder values for local signing and config setup. Keep real keys and machine-local overrides in ignored local files only.

For local development, unsigned or fallback signature workflows can still be useful. For publishable or cross-application flows, prefer Ed25519-backed signing.

## Python facade

The package exports a stable Python surface through `calamum.api`, including helpers to:

- resolve or require project context
- register and validate projects
- list, show, and run definitions
- list and inspect retained runs
- generate, list, and inspect aggregate reports

## Why this repo exists

Calamum packages a reusable testing substrate that gives projects one consistent place to define tests, execute them across multiple validation lanes, and retain evidence worth reviewing later.

Design goals:

- deterministic project-aware execution
- retained evidence instead of terminal-history dependence
- JSON-first machine readability with Markdown companions
- regenerable report surfaces
- credible signing hooks without hardcoding secrets

## Security

For vulnerability reporting and security guidance, see `SECURITY.md`.

## Contributing

Development and contribution guidance lives in `CONTRIBUTING.md`.
