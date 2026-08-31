# AurCounsel MCP

> AurCounsel MCP provides contract review, drafting, comparison, and artifact retrieval through the Model Context Protocol.

AurCounsel MCP is the public developer interface for **AurCounsel**, a contract intelligence platform. It lets MCP-compatible clients submit contract work, monitor asynchronous jobs, and retrieve completed deliverables without exposing AurCounsel's private backend implementation.

**Public MCP endpoint**

```text
https://mcp.clawplus.pro/mcp
```

## What you can do

AurCounsel MCP currently exposes these primary tools:

- `review_contract` — submit a contract for review.
- `draft_contract` — request contract drafting.
- `compare_contracts` — compare two contracts or contract versions.
- `get_job` — inspect the state of an asynchronous job.
- `get_artifact` — retrieve completed deliverables produced by a job.

> **Machine-truth note:** Tool names above are release-accepted. Exact input schemas, response fields, artifact type vocabulary, and executable request examples must be synchronized from the live MCP `tools/list` and production responses before publication.

## Five-minute mental model

Most AurCounsel operations are asynchronous:

```text
MCP Client
   |
   | review_contract / draft_contract / compare_contracts
   v
AurCounsel MCP
   |
   | returns job_id
   v
get_job(job_id)
   |
   | submitted -> processing -> completed
   |                         \\-> failed
   v
get_artifact(...)
```

The basic usage pattern is:

```text
review_contract
-> job_id
-> get_job(job_id)
-> completed
-> get_artifact(...)
```

A job that reaches `failed` is terminal. Partial or internally generated outputs from a failed job are **not** completed deliverables.

## Quickstart

1. Configure an MCP client to use:

   ```text
   https://mcp.clawplus.pro/mcp
   ```

2. Confirm the server exposes the AurCounsel tools.
3. Submit a contract operation such as `review_contract`.
4. Save the returned `job_id`.
5. Poll or re-check with `get_job` until the job is terminal.
6. If the status is `completed`, retrieve the requested deliverable with `get_artifact`.
7. If the status is `failed`, treat the job as failed; do not interpret unavailable artifacts as "still processing."

See [docs/quickstart.md](docs/quickstart.md) for client setup and [docs/job-lifecycle.md](docs/job-lifecycle.md) for lifecycle semantics.

## Documentation

| Document | Purpose |
|---|---|
| [Quickstart](docs/quickstart.md) | Connect an MCP client and complete a first request. |
| [Tools](docs/tools.md) | Public tool contract and schema synchronization points. |
| [Job lifecycle](docs/job-lifecycle.md) | Asynchronous status model and terminal-state rules. |
| [Artifacts](docs/artifacts.md) | Completed deliverables and artifact retrieval semantics. |
| [Errors](docs/errors.md) | Error classes, failed jobs, and client handling. |
| [Architecture](docs/architecture.md) | Public high-level architecture only. |

## Examples

The [`examples/`](examples/) directory contains starter configuration and request examples:

- `claude-desktop.json`
- `cursor.json`
- `python_client.py`
- `curl.md`

Some example fields are deliberately marked for live verification. They must not be presented as executable until checked against the production MCP transport and exact schemas.

## Public interface, not backend source

This repository documents the **public protocol contract**. It does **not** publish the AurCounsel backend, production deployment, private legal corpus, prompts, internal model endpoints, production database structure, or release-validation infrastructure.

The intended public architecture boundary is:

```text
MCP Client
    ↓
AurCounsel MCP
    ↓
AurCounsel Contract Intelligence Engine
    ├── Contract Review
    ├── Drafting
    ├── Comparison
    ├── Legal Grounding
    └── Artifact Generation
```

## Stability and versioning

This repository begins at documentation version **0.1.0**. Until a stable public schema version is declared, consumers should rely on the documented live tool contract and watch [CHANGELOG.md](CHANGELOG.md) for interface changes.

## Security

Do not include credentials, confidential contracts, private fixtures, internal infrastructure details, or production data in public issues or pull requests. See [SECURITY.md](SECURITY.md).

## License

The public repository license has **not yet been selected** for V0.1. Do not publish this repository until `LICENSE` is replaced with the approved license text.
