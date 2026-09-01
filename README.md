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

A live `tools/list` returns exactly these five tools and nothing else. Their exact descriptions, JSON input schemas, response fields, and the artifact vocabulary are transcribed from live captures in [docs/tools.md](docs/tools.md) and [docs/artifacts.md](docs/artifacts.md).

> **Machine-truth note:** the three submission tools create real jobs. Exactly one submission was authorised for this documentation pass — a synthetic, eight-clause contract sent to `review_contract` — and it was followed to completion. Its success-response shape, the exact `job_id` field path, and the `processing` and `completed` job bodies are transcribed from that run. `draft_contract` and `compare_contracts` were never called; their success-response shapes remain **PENDING_AUTH** rather than guessed, and so do the six draft/compare artifact media types. Anything else that was not observed live is marked **UNRESOLVED** in place. Neither marker is a placeholder for a value someone knows — they mark facts this repository does not have.
>
> **Treat a `job_id` as sensitive.** It is the only handle to a job and it is not recoverable. Every identifier in this repository is a placeholder; no real one appears here, and none should appear in an issue, a log, or a chat.

**Transport in one line:** POST JSON-RPC 2.0, send `Accept: application/json, text/event-stream` (both, or HTTP 406) plus your own `User-Agent`, read the reply out of the SSE `data:` line. No credential was required and none is issued. See [docs/quickstart.md](docs/quickstart.md).

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

`python_client.py` runs against the public endpoint with no dependencies beyond the Python standard library, and every command in `curl.md` was executed as written. Both use the obvious placeholder job identifier `0123456789abcdef`, which is well-formed but belongs to no job, so they are safe to run verbatim and end in `JOB_NOT_FOUND`; substitute your own `job_id` to go further. Neither submits work.

The two client configuration files are the exception: the endpoint they name is verified, but no Claude Desktop or Cursor installation was available to load them, so their config shape is marked UNRESOLVED inside the files themselves.

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

[MIT](LICENSE).

The license covers the contents of this repository — the documentation, the examples, and the other files published here. It does not cover, and must not be read as open sourcing, the AurCounsel backend source code, the private legal corpus, or the private Legal Knowledge implementation. Those are not part of this repository and are not published under any license by it.
