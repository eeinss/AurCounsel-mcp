# AurCounsel MCP

> AurCounsel MCP provides contract review, drafting, comparison, legal research, and artifact retrieval through the Model Context Protocol.

AurCounsel MCP is the public developer interface for **AurCounsel**, a contract intelligence platform. It lets MCP-compatible clients submit contract work, monitor asynchronous jobs, and retrieve completed deliverables without exposing AurCounsel's private backend implementation.

> **Newest capability: `fast_legal`.** It answers a legal question with bounded research and says whether the evidence it found was sufficient (`COMPLETE` or `INSUFFICIENT_EVIDENCE`). The optional `level`: `medium` (default) is free and the fastest; `high` is charged by usage; `large` is charged by usage and researches the most deeply. See [Fast Legal](#fast-legal).

> **`compare_contracts` and `revise_contract` are not open.** Both are listed by `tools/list`, and every call returns `PERMISSION_DENIED` with nothing sent. `get_capabilities` says what is open. Revision jobs submitted before `revise_contract` was withdrawn on an earlier date can still be read with `get_job` / `get_artifact` — see [docs/tools.md](docs/tools.md#revise_contract).

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

Requests without a token, or with an invalid one, receive `401 Unauthorized`. Jobs and artifacts are scoped to the authenticated identity. A job or artifact identifier alone does not grant access: reading a job or artifact that belongs to another identity returns `403 Forbidden`. Requests are rate-limited per client IP (120 per 60 seconds; over the limit: `429 Too Many Requests` with `Retry-After`). What a token may submit depends on the capabilities granted to it: a submission the token is not entitled to is refused with `error_code: "UPSTREAM_REJECTED"` and `context.upstream_status: 403`. See [docs/errors.md](docs/errors.md#6-authentication-and-authorization-errors).

## What you can do

AurCounsel MCP currently exposes these primary tools:

- `review_contract` — submit a contract for review.
- `draft_contract` — request contract drafting.
- `compare_contracts` — compare two contracts or contract versions. **Not open yet:** every call returns `PERMISSION_DENIED`.
- `revise_contract` — apply a change to a contract. **Not open yet:** every call returns `PERMISSION_DENIED`.
- `get_capabilities` — what is open right now: capabilities, the models open now (`models`) and built (`implemented_models`), and the contract types each type-limited `draft_contract` model accepts.
- `fast_legal` — answer a legal question with bounded research, together with an evidence-sufficiency status.
- `get_job` — inspect the state of an asynchronous job.
- `get_artifact` — retrieve completed deliverables produced by a job.

A live `tools/list` returns exactly these eight tools and nothing else. The descriptions, JSON input schemas, response fields, and artifact vocabulary are in [docs/tools.md](docs/tools.md) and [docs/artifacts.md](docs/artifacts.md). The live machine-readable contract, not this prose, is canonical.

> **Machine-truth note:** the submission tools create real jobs. Two submissions have been authorised in total, each followed to completion, and each is the sole source of what is written about its tool here:
>
> - `review_contract` — a synthetic, eight-clause contract, in the first documentation pass. Its success-response shape, the exact `job_id` field path, and the `processing` and `completed` job bodies are transcribed from that run.
> - `revise_contract` (since withdrawn) — a synthetic contract plus one explicit revision instruction naming the clause to change, in the revision pass. Its submission arguments, its `submitted` and `completed` job bodies, the `outcome` reporting described below, and the two artifacts it served are transcribed from that run. The contract and the instruction themselves are private fixtures and are not reproduced here.
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
| `review_contract` | `file_name`, one of `file_b64` / `file_ref`, `represented_party`. Optional `model` (a level): `medium` (default); `high` / `large` are built but not open (`PERMISSION_DENIED`) |
| `draft_contract` | `subject` and `requested_jurisdiction`; for a contract (no `doc_type`) also `contract_type` and `represented_party`. Optional `model` (a level): `medium` (default) / `high` / `large`. The contract types with minimum-content guidance are one list for every level, in `get_capabilities`; `high` and `large` draft only those (see [docs/tools.md](docs/tools.md#draft_contract)) |
| `compare_contracts` | not open (`PERMISSION_DENIED`) |
| `revise_contract` | not open (`PERMISSION_DENIED`) |
| `get_capabilities` | none |
| `fast_legal` | `question`. Optional `level`: `medium` (default, free), `high` or `large` (deepest); `high` and `large` are charged by usage |
| `get_article` | `law`, `article` (synchronous; no job, no charge) |
| `search_statutes` | `query`; optional `law`, `level`, `top_k` (synchronous) |
| `search_judgments` | `query`; optional `court`, `top_k` (synchronous) |
| `read_judgment` | `doc_id`, or `court` + `case_number`; optional `around`, `offset`, `max_chars` (synchronous) |
| `get_job` | `job_id` (optional `after_seq` for `fast_legal`) |
| `get_artifact` | `job_id`, `artifact` |

The complete input schemas, the optional arguments, and the constraints the schemas themselves do not express are in [docs/tools.md](docs/tools.md).

`file_ref` handles come from uploading the document to `/upload` first; see [docs/tools.md](docs/tools.md#uploading-a-document-upload).

## Five-minute mental model

Most AurCounsel operations are asynchronous:

```text
MCP Client
   |
   | review_contract / draft_contract / compare_contracts / fast_legal
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

## Job cost

`get_job` reports `cost_status` (`settled` / `not_final` / `unsupported`) and, when settled, `cost: {"amount_micros", "currency": "USD", "final": true}` — the amount the job is settled at, fixed when the job ends. Failed jobs are settled at 0. Settled now: `draft_contract` with `model: "high"` or `"large"`, and `fast_legal` with `level: "high"`; everything else reports `unsupported`. A job interrupted by a service restart is settled at 0. Details: [docs/tools.md](docs/tools.md#cost-cost-cost_status).

## Fast Legal

`fast_legal` performs bounded legal research using AurCounsel's legal retrieval capabilities and returns an answer with an evidence-sufficiency status. A run usually takes one to a few minutes.

`fast_legal` takes `question` and an optional `level` (see [Levels and cost](#levels-and-cost)), and runs asynchronously like the other capabilities.

```bash
curl https://mcp.clawplus.pro/mcp \
  -H "Authorization: Bearer $AURCOUNSEL_MCP_TOKEN" \
  -H 'Content-Type: application/json' \
  -H 'Accept: application/json, text/event-stream' \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "tools/call",
    "params": {
      "name": "fast_legal",
      "arguments": {
        "question": "What must be shown to establish tort liability under Article 184 of the Taiwan Civil Code?"
      }
    }
  }'
```

The reply carries a `job_id`. Poll `get_job` with it; when `status` is `completed`, the answer is in `answer_markdown` and the status in `evidence`. The same Markdown is available as `get_artifact(job_id, "fast_answer")`:

```json
{
  "ok": true,
  "job_id": "0123456789abcdef",
  "capability": "fast_legal",
  "status": "completed",
  "progress": null,
  "answer_markdown": "...",
  "evidence": {
    "status": "COMPLETE",
    "insufficiency_reason": "",
    "review_outcome": "PASS"
  },
  "draft_check": {"class": "A", "changes": 0},
  "sources": [ ... ],
  "sources_summary": { ... },
  "artifacts": [{"name": "fast_answer", "ready": true}],
  "level": "medium",
  "cost": null,
  "cost_status": "unsupported"
}
```

| `evidence` field | Meaning |
| --- | --- |
| `status` | `COMPLETE` — the evidence found supports the core answer (it does not mean the research was exhaustive). `INSUFFICIENT_EVIDENCE` — only part of the answer could be supported; the answer states what could and could not be confirmed, and why. |
| `insufficiency_reason` | Set only for `INSUFFICIENT_EVIDENCE`: what is missing and why. |
| `review_outcome` | Observability only: which internal review result produced the status (`PASS`, `REWRITE`, `INSUFFICIENT_EVIDENCE`, `NOT_RUN`, `UNREADABLE`). |

The status is **model-assessed**, not a guarantee. `INSUFFICIENT_EVIDENCE` does not mean the proposition is false or that no authority exists; it means bounded research did not gather enough to answer reliably.

`evidence.status` is the answer review's own result. It is not a legal verification of the answer, and the answer text carries no evidence-status line. How to present `evidence` is up to the client: see [Presenting evidence and sources](docs/tools.md#presenting-evidence-and-sources).

### Levels and cost

| `level` | Research | Charge |
| --- | --- | --- |
| `medium` (default) | The fastest | None: `cost: null`, `cost_status: "unsupported"`. |
| `high` | Deeper than `medium` | By usage (as `large`). |
| `large` | The deepest research | By usage: once the job is `completed` or `failed`, `cost: {"amount_micros", "currency": "USD", "final": true}` with `cost_status: "settled"` (`not_final` while it is processing; a failed job is settled at 0). |

Any other `level` is refused with `INVALID_INPUT` and `context: {"field": "level"}`. `get_job` returns the job's `level`. `answer_markdown` is the answer alone; it carries no cost line. Details: [docs/tools.md](docs/tools.md#levels-and-cost-level-cost-cost_status).

### Sources

A completed `fast_legal` job also returns `sources`: the statutes and judgments `answer_markdown` cites, each with `cited_as` (the citation as written in the answer) and `retrieval`, which says what this job actually obtained. For a statute that is `text` (looked up by name), `excerpt`, `listed` or `not_retrieved`; for a judgment it is `read` (with `full_text.complete`), `excerpt`, `listed`, `cited_in_retrieved_judgment` or `not_retrieved`. Retrieved texts are included as returned, and `text_truncated` is `true` when a statute's text was cut short. Nothing is generated: a citation the job's retrieval record does not show as retrieved is `not_retrieved`, with its content `null`. `sources: null` (for example on older jobs) means no source data is delivered for that job, not that it did no retrieval. Sources follow the final answer, not the streamed draft; read them together with `answer_markdown` from the `completed` reply. A listed source does not mean the analysis is correct. Details: [docs/tools.md](docs/tools.md#sources-sources-sources_summary).

### Following the answer as it is written

Pass `after_seq` to `get_job` (0 first, then the `last_seq` of the previous reply) to receive the job's progress steps and the answer text while it is being written. Only events after `after_seq` are returned, so polling again repeats nothing. The streamed text is a draft: when the job is `completed`, `answer_markdown` replaces it, and `draft_check.class` is `C` when the evidence review rewrote it. A failed job's draft is not an answer. Events are kept for one hour after the job ends. Clients that do not send `after_seq` get the same reply as before. Details: [docs/tools.md](docs/tools.md#following-a-fast_legal-job-as-it-runs-after_seq).

Like every job, a Fast Legal job is readable only by the identity that submitted it.

## Quickstart

1. Configure an MCP client to use the endpoint below, with the header `Authorization: Bearer <AURCOUNSEL_MCP_TOKEN>` on every request:

   ```text
   https://mcp.clawplus.pro/mcp
   ```

2. Confirm the server exposes the AurCounsel tools.
3. Submit a contract operation such as `review_contract`, or a legal question with `fast_legal`.
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
    ├── Legal Research (Fast Legal, Legal Research)
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
