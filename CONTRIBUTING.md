# Contributing

<p align="center">
	<img src="assets/branding/polymath_global.png" alt="Polymath Global logo" width="140">
</p>

<p align="center">
	<a href="https://polymath-global.com">polymath-global.com</a>
</p>

Thanks for helping improve `Calamum Test`. Keep user-facing behavior, retained-evidence outputs, and public docs in sync so the published package stays truthful and easy to review.

## Development setup

From `projects/calamum/`:

1. create or activate a Python environment
2. install the package in editable mode with dev extras
3. run the validation lanes before proposing changes

Suggested bootstrap commands:

- `python -m pip install -e .[dev]`
- `calamum --version`
- `calamum -h`

## Local validation expectations

Minimum routine validation:

- `python -m pytest`
- CLI smoke checks for the surface you changed
- report generation checks when reporting or security behavior changes

Add these checks when they match the surface you touched:

- `calamum test -h`
- `calamum project -h`
- `calamum monitor -h`
- `calamum test list --json`
- `python -m build --wheel --sdist`
- `python -m twine check dist/*`

## Public-facing documentation expectations

- `README.md` is the primary user-facing install, naming, and command-surface guide.
- `CHANGELOG.md` records shipped public behavior; do not rebadge the active release version until the explicit cutover step.
- `SECURITY.md` and `.env.example` must stay aligned with the current signing and configuration surface.
- Update public docs whenever command families, package naming, output layout, security expectations, or release steps change.

## Project conventions

- keep the CLI JSON-first and easy to read
- keep project descriptors portable and secret-free
- prefer deterministic paths and reproducible reports
- add tests with each new surface
- keep generated outputs and machine-local state out of shared history

## Release checklist

For release maintainers, verify the following before publishing:

- clean stale `dist/` artifacts before rebuilding
- build `sdist` and `wheel`
- run `twine check`
- confirm console-script behavior
- confirm `calamum --version` reports the release candidate version
- confirm install and runtime names are documented correctly (`calamum-test` -> `calamum`)
- confirm `README.md`, `CHANGELOG.md`, `CONTRIBUTING.md`, and `SECURITY.md` match the shipped surface
- if releasing from the umbrella workspace, confirm the standalone public-repo sync route before index publication
- review package metadata and rendered documentation
