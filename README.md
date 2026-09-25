# AurCounsel MCP

> AurCounsel MCP provides contract review, drafting, comparison, revision, and artifact retrieval through the Model Context Protocol.

AurCounsel MCP is the public developer interface for **AurCounsel**, a contract intelligence platform. It lets MCP-compatible clients submit contract work, monitor asynchronous jobs, and retrieve completed deliverables without exposing AurCounsel's private backend implementation.

> **Newest capability: `revise_contract`.** It takes a contract plus a revision instruction in prose and returns the revised document together with a tracked-change redline. It is the one capability whose result is **not** carried by `status`: a revision that was applied and a revision the server declined to apply both finish as `completed`, and the difference is reported on a separate `outcome` field. See [What you can do](#what-you-can-do) and the revision notes in [docs/quickstart.md](docs/quickstart.md).

**Public MCP endpoint**

```text
https://mcp.clawplus.pro/mcp
```

## Authentication

Every MCP request must carry a bearer token:

```text
Authorization: Bearer <AURCOUNSEL_MCP_TOKEN>
```

Keep the token in an environment variable rather than in files or command history:

```bash
export AURCOUNSEL_MCP_TOKEN="..."
```

Requests without a token, or with an invalid one, receive `401 Unauthorized`. Jobs and artifacts are scoped to the authenticated identity. A job or artifact identifier alone does not grant access: reading a job or artifact that belongs to another identity returns `403 Forbidden`. See [docs/errors.md](docs/errors.md#6-authentication-and-authorization-errors).

## What you can do

AurCounsel MCP currently exposes these primary tools:

- `review_contract` — submit a contract for review.
- `draft_contract` — request contract drafting.
- `compare_contracts` — compare two contracts or contract versions.
- `revise_contract` — submit a contract plus a revision instruction, and get the revised contract and a tracked-change redline back.
- `get_job` — inspect the state of an asynchronous job.
- `get_artifact` — retrieve completed deliverables produced by a job.

A live `tools/list` returns exactly these six tools and nothing else. The descriptions, JSON input schemas, response fields, and artifact vocabulary are in [docs/tools.md](docs/tools.md) and [docs/artifacts.md](docs/artifacts.md). The live machine-readable contract, not this prose, is canonical.

> **Machine-truth note:** the four submission tools create real jobs. Two submissions have been authorised in total, each followed to completion, and each is the sole source of what is written about its tool here:
>
> - `review_contract` — a synthetic, eight-clause contract, in the first documentation pass. Its success-response shape, the exact `job_id` field path, and the `processing` and `completed` job bodies are transcribed from that run.
> - `revise_contract` — a synthetic contract plus one explicit revision instruction naming the clause to change, in the revision pass. Its submission arguments, its `submitted` and `completed` job bodies, the `outcome` reporting described below, and the two artifacts it served are transcribed from that run. The contract and the instruction themselves are private fixtures and are not reproduced here.
>
> `draft_contract` and `compare_contracts` were never called; their success-response shapes remain **PENDING_AUTH** rather than guessed, and so do the six draft/compare artifact media types. Anything else that was not observed live is marked **UNRESOLVED** in place. Neither marker is a placeholder for a value someone knows — they mark facts this repository does not have.
>
> **Treat a `job_id` and your token as sensitive.** A `job_id` is not recoverable, and jobs are readable only by the identity that submitted them. Every identifier in this repository is a placeholder; no real identifier or token appears here, and none should appear in an issue, a log, or a chat.

**Transport in one line:** POST JSON-RPC 2.0 with `Authorization: Bearer $AURCOUNSEL_MCP_TOKEN`, send `Accept: application/json, text/event-stream` (both, or HTTP 406) plus your own `User-Agent`, read the reply out of the SSE `data:` line. See [docs/quickstart.md](docs/quickstart.md).

## API / Wire format

Every operation is a JSON-RPC 2.0 call to the same endpoint:

```text
POST https://mcp.clawplus.pro/mcp
```

Required headers:

```text
Authorization: Bearer <AURCOUNSEL_MCP_TOKEN>
Content-Type: application/json
Accept: application/json, text/event-stream
```

Both `Accept` values must be present, or the server answers HTTP 406. Send your own `User-Agent` as well; the edge network rejects some default agent strings with HTTP 403 before the request reaches the server.

A tool call uses this envelope:

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "tools/call",
  "params": {
    "name": "get_job",
    "arguments": {
      "job_id": "0123456789abcdef"
    }
  }
}
```

The same call with `curl`:

```bash
export AURCOUNSEL_MCP_TOKEN="..."

curl https://mcp.clawplus.pro/mcp \
  -H "Authorization: Bearer $AURCOUNSEL_MCP_TOKEN" \
  -H 'Content-Type: application/json' \
  -H 'Accept: application/json, text/event-stream' \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "tools/call",
    "params": {
      "name": "get_job",
      "arguments": {
        "job_id": "0123456789abcdef"
      }
    }
  }'
```

The reply is an `event: message` SSE frame; the JSON-RPC response is the JSON on its `data:` line.

Required arguments, by tool:

| Tool | Required arguments |
| --- | --- |
| `review_contract` | `file_name`, `file_b64` |
| `draft_contract` | `subject` |
| `compare_contracts` | `file_a_name`, `file_a_b64`, `file_b_name`, `file_b_b64` |
| `revise_contract` | `file_name`, one of `file_b64` / `file_ref`, `revision_text` |
| `get_job` | `job_id` |
| `get_artifact` | `job_id`, `artifact` |

The complete input schemas, the optional arguments, and the constraints the schemas themselves do not express are in [docs/tools.md](docs/tools.md).

`revise_contract` takes the document either inline as `file_b64` or by reference as `file_ref`; supply one of the two, not both. `revision_text` is the revision instruction, in prose: name the clause you want changed and say what it should say. An instruction the server cannot tie to a clause in the submitted contract is not an error; it comes back as a `completed` job that declined to revise, with the reason on the `outcome` field. See [docs/quickstart.md](docs/quickstart.md).

## Five-minute mental model

Most AurCounsel operations are asynchronous:

```text
MCP Client
   |
   | review_contract / draft_contract / compare_contracts / revise_contract
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

A revision runs the same loop, with one extra thing to read at the end:

```text
revise_contract(file_name, file_b64, revision_text)
-> job_id
-> get_job(job_id)
-> completed
-> read the outcome: applied, or declined with a reason
-> get_artifact(...)   # revised_docx, redline_docx
```

A job that reaches `failed` is terminal. Partial or internally generated outputs from a failed job are **not** completed deliverables.

For a revision, `completed` answers "did the job finish", not "was the contract changed". Those are two different questions and the server answers them on two different fields — see [docs/quickstart.md](docs/quickstart.md#6-check-job-status).

## Quickstart

1. Configure an MCP client to use the endpoint below, with the header `Authorization: Bearer <AURCOUNSEL_MCP_TOKEN>` on every request:

   ```text
   https://mcp.clawplus.pro/mcp
   ```

2. Confirm the server exposes the AurCounsel tools.
3. Submit a contract operation such as `review_contract`, or `revise_contract` with a revision instruction.
4. Save the returned `job_id`.
5. Poll or re-check with `get_job` until the job is terminal.
6. If the status is `completed`, retrieve the requested deliverable with `get_artifact`. For a revision, read the `outcome` field first: `completed` alone does not mean the contract was changed.
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

`python_client.py` runs against the public endpoint with no dependencies beyond the Python standard library, and every command in `curl.md` was executed as written. Both read the token from `AURCOUNSEL_MCP_TOKEN` and use the obvious placeholder job identifier `0123456789abcdef`, which is well-formed but belongs to no identity, so they are safe to run verbatim and end in `403 Forbidden`; substitute a `job_id` your identity submitted to go further. Neither submits work.

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
    ├── Revision
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
