# Security policy

<p align="center">
	<img src="assets/branding/calamum_logo_color.png" alt="Calamum logo" width="220">
</p>

`Calamum Test` includes reporting, signing, and verification features that should be treated as security-relevant surfaces.

## Reporting a vulnerability

Please report vulnerabilities privately to the maintainers before opening a public issue. Include:

- affected version
- reproduction steps
- expected vs actual behavior
- whether signing, delegated requests, or retained evidence integrity is involved

Do not post exploit details, signing material, or sensitive local paths in a public issue first.

## Security expectations

- never commit secrets, signing keys, or machine-local overlays
- use environment variables or ignored local files for signing configuration
- keep `.calamum/project.json` free of secrets and host-specific credentials
- keep local signing paths and `.env` data out of shared history
- use `.env.example` as a placeholder reference only; replace with local ignored values before testing signing flows
- verify detached signatures before relying on signed outputs
- fail closed when verification, allowlist, or containment checks fail

## Release hygiene

- treat `.calamum/generated/`, `runs/`, `reports/`, and local overlays as local-only evidence or machine state unless a workflow explicitly says otherwise
- review rendered package metadata and `twine check` output before public publication
- re-check the live CLI help surface after changing command families, signing flows, or retained-output contracts

## Relevant environment variables

- `CALAMUM_ED25519_PRIVATE_KEY`
- `CALAMUM_ED25519_PUBLIC_KEY`
- `CALAMUM_POLICY_SIGNING_KEY`
- `CALAMUM_CONFIG_ROOT`

For local development, fallback signatures are supported. For release and shared verification workflows, prefer Ed25519.
