# Repository Information Architecture — V0.1

## Audience

Primary: engineers integrating AurCounsel through MCP.

Secondary: security reviewers, platform teams, and developers debugging public integration behavior.

## Five-minute path

A new engineer should be able to follow this path:

```text
README
  -> Quickstart
  -> live tool discovery
  -> submit operation
  -> Job lifecycle
  -> Artifacts
  -> Errors (when needed)
```

## Information layers

### Layer 1 — Orientation

- `README.md`
- product capability statement
- endpoint
- five primary tools
- basic async flow
- public/private boundary

### Layer 2 — First successful integration

- `docs/quickstart.md`
- `examples/*`

### Layer 3 — Protocol contract

- `docs/tools.md`
- `docs/job-lifecycle.md`
- `docs/artifacts.md`
- `docs/errors.md`

### Layer 4 — Trust / maintenance

- `docs/architecture.md`
- `SECURITY.md`
- `CHANGELOG.md`
- `LICENSE`

### Pre-publication work aid

- `MACHINE_TRUTH_CHECKLIST.md`

This file may remain internal to the draft branch or be removed before public release.
