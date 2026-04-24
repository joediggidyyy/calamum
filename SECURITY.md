# Security policy

<p align="center">
	<img src="assets/branding/calamum_logo_color.png" alt="Calamum logo" width="220">
</p>

`Calamum Test` treats retained evidence and privileged aggregate generation as security-relevant surfaces.

## Reporting a vulnerability

Please report vulnerabilities privately to the maintainers before opening a public issue. Include:

- affected version
- reproduction steps
- expected vs actual behavior
- whether signing, delegated requests, or retained evidence integrity is involved

## Security expectations

- never commit secrets, signing keys, or machine-local overlays
- use environment variables or ignored local files for signing configuration
- keep `.calamum/project.json` free of secrets and host-specific credentials
- keep local signing paths and `.env` data out of shared history
- verify detached signatures before privileged aggregate generation
- fail closed when verification, allowlist, or containment checks fail

## Relevant environment variables

- `CALAMUM_ED25519_PRIVATE_KEY`
- `CALAMUM_ED25519_PUBLIC_KEY`
- `CALAMUM_POLICY_SIGNING_KEY`
- `CALAMUM_CONFIG_ROOT`

Development fallback signatures are supported for local use, but publishable or privileged flows should prefer Ed25519.
