# Contributing

<p align="center">
	<img src="assets/branding/polymath_global.png" alt="Polymath Global logo" width="240">
</p>

## Development setup

From `projects/calamum/`:

1. create or activate a Python environment
2. install the package in editable mode with dev extras
3. run the validation lanes before proposing changes

## Local validation expectations

Minimum routine validation:

- `pytest`
- project-aware CLI smoke checks
- aggregate report generation checks when report/security code changes

## Project conventions

- keep the CLI JSON-first and operator-readable
- preserve retained evidence instead of relying on terminal history
- keep project descriptors portable and secret-free
- prefer deterministic paths and regenerable reports
- add tests with each new surface

## Packaging and release hygiene

Before a release-oriented change is considered ready:

- clean stale `dist/` artifacts before rebuilding
- build `sdist` and `wheel`
- run `twine check`
- confirm console-script behavior
- confirm `calamum --version` reports the release candidate version
- confirm the install/runtime name split is documented (`calamum-test` -> `calamum`)
- confirm detached signatures and receipt flows where applicable
