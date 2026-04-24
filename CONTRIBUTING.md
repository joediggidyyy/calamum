# Contributing

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

- build `sdist` and `wheel`
- run `twine check`
- confirm console-script behavior
- confirm detached signatures and receipt flows where applicable
