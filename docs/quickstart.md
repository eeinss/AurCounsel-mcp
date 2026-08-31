# Quickstart

This guide is designed for an engineer who has never used AurCounsel before. The goal is to connect an MCP client, submit one contract operation, observe the job lifecycle, and retrieve a completed artifact.

## 1. Endpoint

AurCounsel MCP is available at:

```text
https://mcp.clawplus.pro/mcp
```

The production endpoint may retain the `clawplus.pro` domain while the product brand is **AurCounsel**.

Transport, as observed live:

| Property | Value |
|---|---|
| Protocol | JSON-RPC 2.0 over HTTP POST |
| MCP protocol version | `2025-06-18` |
| Request `Content-Type` | `application/json` |
| Request `Accept` | `application/json, text/event-stream` — **both**, or HTTP 406 |
| Response content type | `text/event-stream` (an `event: message` frame with a `data:` line) |
| Session header | none; no `Mcp-Session-Id` is issued or expected |
| `User-Agent` | must be set to something; see below |

The server identifies itself in `initialize` as:

```json
"serverInfo": {"name": "legalos", "version": "1.27.0"}
```

> `legalos` is the **server identifier** the live deployment returns — a compatibility identifier for clients that key off `serverInfo.name`. It is not the product name. The product is **AurCounsel**; this repository reproduces server-emitted strings exactly as received and never rewrites them. See [tools.md](tools.md).

## 2. Prerequisites

You need:

- an MCP-compatible client, or any HTTP client that can POST JSON;
- network access to the public endpoint.

**Authentication:** none observed. `tools/list` succeeded with no `Authorization` header, and returned the identical five-tool list when sent `Authorization: Bearer not-a-real-token`. There is no credential to obtain, and no auth error envelope exists to document.

> **Caution.** That is a statement of observed behavior, not a recommendation. Do not read "no credential was required" as "this data is public." A `job_id` is the only handle to a job and grants access to that job's artifacts — the live server instructions say to treat it as a credential. Whether the artifact download URLs are separately guarded was not tested; see [artifacts.md](artifacts.md).

**User agent:** send one. The edge network in front of the endpoint rejects Python's default `Python-urllib/*` signature with HTTP 403 (Cloudflare error 1010) before the request reaches the MCP server. Any identifying value works; `curl`'s default is accepted. See [errors.md](errors.md).

## 3. Configure your MCP client

Use the public endpoint as the MCP server URL.

Example client files are available in:

- [`../examples/claude-desktop.json`](../examples/claude-desktop.json)
- [`../examples/cursor.json`](../examples/cursor.json)

These files intentionally isolate endpoint configuration from private implementation details.

> **UNRESOLVED — client config syntax.** The endpoint was verified live; the two config files were not. Neither Claude Desktop nor Cursor was available to load them during verification, and MCP client configuration formats change between client versions. Both files are marked accordingly. Check your client's current documentation for how it declares a remote HTTP MCP server.

A dependency-free client that does work end to end, using only the Python standard library, is [`../examples/python_client.py`](../examples/python_client.py). Raw requests are in [`../examples/curl.md`](../examples/curl.md).

## 4. Discover the tools

After connecting, confirm the server exposes the expected primary tools:

```text
review_contract
draft_contract
compare_contracts
get_job
get_artifact
```

A live `tools/list` returns exactly these five and nothing else. `prompts/list` returns `{"prompts": []}` and `resources/list` returns `{"resources": []}` — the server publishes no prompts and no resources.

The canonical schemas are whatever the live MCP server returns through tool discovery. The prose documentation in this repo must be regenerated or corrected whenever it diverges from that machine-readable contract. Every schema in [tools.md](tools.md) was transcribed from a live capture.

## 5. Submit a job

Choose one operation. For example, a contract review:

```text
review_contract(file_name, file_b64, [requested_jurisdiction], [represented_party], [contract_type_hint])
```

`file_name` and `file_b64` are the required fields; `file_b64` is the base64 of a `.docx`. The full schema for each submission tool is in [tools.md](tools.md).

A successful submission returns enough information to identify the asynchronous job, including a `job_id`. The `job_id` is not a top-level JSON-RPC field: it is inside the text content block, which is itself a JSON document.

```text
result.content[0].text  ->  parse as JSON  ->  job_id
```

That path, and the full success-response body, are recorded in [tools.md](tools.md) from one authorised `review_contract` submission.

> **PENDING_AUTH — the other two submission tools.** Calling `draft_contract` or `compare_contracts` creates a real job in the production system, and neither was called. Their success-response shapes are **not** recorded here and are not assumed to match `review_contract`'s. Both are marked PENDING_AUTH in [tools.md](tools.md). Nothing on this page invents them.

The `job_id` is the only handle to the job and is not recoverable. Store it before you do anything else, and treat it as a credential.

## 6. Check job status

Use:

```text
get_job(job_id)
```

Public lifecycle vocabulary:

```text
submitted
processing
completed
failed
unknown
```

The client should continue checking only while the job is non-terminal. `completed` and `failed` are terminal outcomes.

`unknown` does **not** mean the job could not be found. It means the engine reported a state this server does not map; the raw value is in `upstream_status` and `status_recognised` is `false`. An identifier that resolves to no job produces a `JOB_NOT_FOUND` application error instead — a different thing entirely. Neither `unknown` nor `JOB_NOT_FOUND` should be treated as progress.

See [job-lifecycle.md](job-lifecycle.md) for full semantics.

## 7. Retrieve artifacts

Once a job reaches `completed`, request a completed deliverable with:

```text
get_artifact(job_id, artifact)
```

The second argument is named `artifact` (not `artifact_type`) and must be one of exactly twelve values. Both are verified live. The response reports `available`, `media_type`, a download `url`, and — for text artifacts — the content inline in `text`; binary artifacts return `text: null`. See [artifacts.md](artifacts.md) for the vocabulary, the response fields, and the failed-job behavior.

If a job reaches `failed`, partial/generated internal outputs are not considered completed deliverables and should not be consumed as if the job succeeded.

## 8. Minimal client algorithm

```text
submit operation
    ↓
receive job_id
    ↓
get_job(job_id)
    ↓
submitted or processing? ── yes ──> check again later
    │
    no
    ↓
completed? ── yes ──> get_artifact(...)
    │
    no
    ↓
failed or unknown -> stop and handle error
```

Working code for the read side of this loop is in [`../examples/python_client.py`](../examples/python_client.py).

## Verification status of this guide

Executed live against the public endpoint during this documentation pass:

- `initialize`, `tools/list`, `prompts/list`, `resources/list`;
- exact description and JSON input schema for all five tools;
- one `review_contract` submission of a synthetic contract, followed by ten `get_job` reads to `completed`;
- `get_job` on a `processing` job, on a `completed` job, and on a terminally `failed` job;
- `get_artifact` for all six artifacts of a completed review job, including a binary one;
- unknown job, malformed job identifier, unknown artifact name, unknown tool, unknown method, malformed JSON, missing `Accept`, and rejected user agent;
- requests with no credential and with a bogus bearer token.

Still outstanding:

- **PENDING_AUTH** — `draft_contract` and `compare_contracts`: their success responses, the six draft/compare artifact media types, and the `PARTY_CONFIRMATION_REQUIRED` refusal. Both write to production and neither was called.
- **UNRESOLVED** — a `get_job` response carrying `submitted` (the first poll, 16 seconds in, already read `processing`), the two client configuration files, artifact-URL access control, and rate-limit or retry-hint behavior.
