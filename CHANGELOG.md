# Changelog

## 0.3.0 - 2026-05-02

### Added

- top-level `calamum project` command family
- top-level `calamum monitor` command family with truthful capability scaffolding
- `calamum --version` for direct installed-version verification
- release audit script at `tools/release_version_audit.py`

### Changed

- package metadata now derives version from `calamum.__version__`
- README now documents the install/runtime split explicitly:
  - install from PyPI as `calamum-test`
  - run the CLI as `calamum`
- contributing guidance now includes release hygiene checks for stale build artifacts and version verification

### Compatibility

- `calamum test project ...` remains available as a compatibility alias during the current route migration
- retained `monitor` behavior remains intentionally scaffolded and should not be interpreted as full monitor execution parity
