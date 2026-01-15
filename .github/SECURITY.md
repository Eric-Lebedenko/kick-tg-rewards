# Security Policy

## Reporting
- Please report vulnerabilities privately to [@Eric-Lebedenko](https://github.com/Eric-Lebedenko).
- Do not open public issues for security reports.
- Provide: affected endpoints/flows, reproduction steps, expected/actual behavior, impact.

## Scope
- This repository’s code and deployment configs.
- OAuth keys, tokens, and secrets must never be committed. Use `.env` locally.

## Best practices
- Keep dependencies up to date (Dependabot enabled).
- Use HTTPS endpoints for bot/webhooks.
- Rotate secrets if you suspect exposure.
