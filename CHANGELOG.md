# Changelog

## 0.3.1 - 2026-05-03

### Added

- top-level `calamum project` command family
- top-level `calamum monitor` command family
- `calamum --version`
- release audit script at `tools/release_version_audit.py`

### Changed

- package metadata now derives version from `calamum.__version__`
- README now documents the install/runtime naming clearly:
  - install from PyPI as `calamum-test`
  - run the CLI as `calamum`
- contributing guidance now includes an updated release checklist
- public support docs now align more explicitly with signing placeholders, project-aware retained outputs, and release validation expectations

### Compatibility

- `calamum test project ...` remains available as a compatibility alias
