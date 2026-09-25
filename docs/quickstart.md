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

**Authentication:** every MCP request must carry a bearer token, including `initialize`, `tools/list`, every `tools/call`, and artifact downloads:

```text
Authorization: Bearer <AURCOUNSEL_MCP_TOKEN>
```

```bash
export AURCOUNSEL_MCP_TOKEN="..."
```

A request without a token, or with an invalid one, receives `401 Unauthorized`. Jobs and artifacts are scoped to the authenticated identity: a job or artifact identifier alone does not grant access, and reading another identity's job or artifact returns `403 Forbidden`. See [errors.md](errors.md#6-authentication-and-authorization-errors).

**User agent:** send one. The edge network in front of the endpoint rejects Python's default `Python-urllib/*` signature with HTTP 403 (Cloudflare error 1010) before the request reaches the MCP server. Any identifying value works; `curl`'s default is accepted. See [errors.md](errors.md).

## 3. Configure your MCP client

Use the public endpoint as the MCP server URL, and configure the client to send `Authorization: Bearer <AURCOUNSEL_MCP_TOKEN>` on every request.

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
revise_contract
get_job
get_artifact
```

A live `tools/list` returns exactly these six and nothing else. `prompts/list` returns `{"prompts": []}` and `resources/list` returns `{"resources": []}` — the server publishes no prompts and no resources.

The canonical schemas are whatever the live MCP server returns through tool discovery. The prose documentation in this repo must be regenerated or corrected whenever it diverges from that machine-readable contract. The per-tool contract is in [tools.md](tools.md).

### A request you can paste as-is

Every tool is invoked the same way: a JSON-RPC 2.0 `tools/call` POST to the endpoint. This one reads a job, so it changes nothing:

```http
POST /mcp HTTP/1.1
Host: mcp.clawplus.pro
Authorization: Bearer <AURCOUNSEL_MCP_TOKEN>
Content-Type: application/json
Accept: application/json, text/event-stream

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

The same request with `curl`:

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
      "name": "get_job",
      "arguments": {
        "job_id": "0123456789abcdef"
      }
    }
  }'
```

The response is not plain JSON. It arrives as `text/event-stream`: an `event: message` frame whose `data:` line carries the JSON-RPC response, which your client must read out of that line before parsing.

`0123456789abcdef` is a well-formed identifier that belongs to no identity, so this request is safe to run verbatim and ends in `403 Forbidden`. Substitute a `job_id` your identity submitted to read a real job.

## 5. Submit a job

Choose one operation. For example, a contract review:

```text
review_contract(file_name, file_b64, [requested_jurisdiction], [represented_party], [contract_type_hint])
```

`file_name` and `file_b64` are the required fields; `file_b64` is the base64 of a `.docx`. The full schema for each submission tool is in [tools.md](tools.md).

On the wire, that submission is:

```http
POST /mcp HTTP/1.1
Host: mcp.clawplus.pro
Authorization: Bearer <AURCOUNSEL_MCP_TOKEN>
Content-Type: application/json
Accept: application/json, text/event-stream

{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "tools/call",
  "params": {
    "name": "review_contract",
    "arguments": {
      "file_name": "example-agreement.docx",
      "file_b64": "<base64 of your .docx>"
    }
  }
}
```

**Executing this request creates a production job.** Unlike the `get_job` request above, it is not safe to run as a demonstration: it consumes real processing and returns a `job_id` you must keep.

A successful submission returns enough information to identify the asynchronous job, including a `job_id`. The `job_id` is not a top-level JSON-RPC field: it is inside the text content block, which is itself a JSON document.

```text
result.content[0].text  ->  parse as JSON  ->  job_id
```

That path, and the full success-response body, are recorded in [tools.md](tools.md) from one authorised `review_contract` submission.

> **PENDING_AUTH — the other two submission tools.** Calling `draft_contract` or `compare_contracts` creates a real job in the production system, and neither was called. Their success-response shapes are **not** recorded here and are not assumed to match `review_contract`'s. Both are marked PENDING_AUTH in [tools.md](tools.md). Nothing on this page invents them.

The `job_id` is the only handle to the job and is not recoverable. Store it before you do anything else, and treat it as a credential.

### Submitting a revision

`revise_contract` takes a contract and an instruction describing the change you want:

```text
revise_contract(file_name, file_b64 | file_ref, revision_text)
```

`file_b64` is the base64 of a `.docx`, as for a review; `file_ref` is the alternative to it, a reference to the document instead of its bytes. Send one of the two. `revision_text` is the instruction, in prose. On the wire:

```http
POST /mcp HTTP/1.1
Host: mcp.clawplus.pro
Authorization: Bearer <AURCOUNSEL_MCP_TOKEN>
Content-Type: application/json
Accept: application/json, text/event-stream

{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "tools/call",
  "params": {
    "name": "revise_contract",
    "arguments": {
      "file_name": "example-agreement.docx",
      "file_b64": "<base64 of your .docx>",
      "revision_text": "<name the clause to change, and say what it should say>"
    }
  }
}
```

**This also creates a production job.** The submission that was observed returned, inside the text content block, a `job_id` alongside `status: "submitted"`, `capability: "revise"`, and `detected_kind: "docx"` — so the `job_id` field path is the same one the review flow uses, and the job is read back with the same `get_job`.

**Write the instruction so it names the clause.** An instruction the server cannot tie to a clause in the submitted document does not fail: the job still reaches `completed`, and it reports that it declined to revise, with a reason. That reporting is the next section.

**How a clause is located.** A clause number is the authoritative locator. If the instruction names an ordinal that exists in the document — `第三條`, clause 3 — that clause is where the revision is applied, and the rest of the instruction cannot move it: any description of the clause's subject or title can only help locate a clause, never override an ordinal that the document actually has. An ordinal the document does not have is a different case: nothing is guessed, and the job comes back `completed` having declined to revise, with the reason.

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

### For a revision, read the outcome as well as the status

A `revise_contract` job carries `capability: "revise"` and one field the other capabilities do not: `revision`, a nested object beside `status` in the same parsed content block.

This matters because `status` does not answer the question you actually asked. A revision that was applied and a revision the server declined to apply are **both** `completed`. The difference is reported only on `revision.outcome`:

| Field | Type | Meaning |
|---|---|---|
| `outcome` | string | What happened to the revision. See the values below. |
| `outcome_recognised` | boolean | Whether the server mapped the engine's own outcome value into its published vocabulary — the same self-report idea as `status_recognised`. |
| `replaced` | integer | How many clauses were replaced. |
| `not_applied` | integer | How many requested changes were not applied. |
| `reason` | string \| null | User-facing explanation when the revision was not applied; `null` when it was applied. |

Outcome values:

- `applied` — the revision was made. `replaced` counts the clauses that were replaced, `not_applied` is zero, and `reason` is null.
- `needs_clarification` — the server could not tie the instruction to a clause in the submitted contract and did not revise. The job is still `completed`, and `reason` carries the explanation to show the user.
- `blocked` — the third value in the server's recognised set.

A client that branches on `status` alone will report a declined revision as a success. Branch on `outcome`, and surface `reason` to the user when it is non-null.

## 7. Retrieve artifacts

Once a job reaches `completed`, request a completed deliverable with:

```text
get_artifact(job_id, artifact)
```

The second argument is named `artifact` (not `artifact_type`). The response reports `available`, `media_type`, a download `url`, and — for text artifacts — the content inline in `text`; binary artifacts return `text: null`. See [artifacts.md](artifacts.md) for the vocabulary, the response fields, and the failed-job behavior.

A completed revision lists its deliverables in the job's own `artifacts[]`, each with a `name` and a `ready` flag; fetch by the names you find there. A revision serves two:

- `revised_docx` — the revised contract, as a `.docx`.
- `redline_docx` — the same revision as a tracked-change `.docx`. It carries real Word tracked changes (insertion and deletion revision marks), not just visually marked-up text, so it opens in Word with the changes reviewable and acceptable/rejectable.

Do not confuse `redline_docx` with `redline`: a review's `redline` is an HTML view of the changes, while `redline_docx` is a Word document carrying the changes as revision marks.

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

For a `revise` job, insert one step between `completed?` and `get_artifact(...)`: read `revision.outcome`. If it is not `applied`, the job succeeded but the contract was not changed — report `revision.reason` instead of presenting artifacts as a revision.

Working code for the read side of this loop is in [`../examples/python_client.py`](../examples/python_client.py).

## Verification status of this guide

Executed live against the public endpoint in the first documentation pass:

- `initialize`, `tools/list`, `prompts/list`, `resources/list`;
- exact description and JSON input schema for `review_contract`, `draft_contract`, `compare_contracts`, `get_job`, and `get_artifact`;
- one `review_contract` submission of a synthetic contract, followed by ten `get_job` reads to `completed`;
- `get_job` on a `processing` job, on a `completed` job, and on a terminally `failed` job;
- `get_artifact` for all six artifacts of a completed review job, including a binary one;
- unknown job, malformed job identifier, unknown artifact name, unknown tool, unknown method, malformed JSON, missing `Accept`, and rejected user agent;
- requests with no credential and with a bogus bearer token (at the time, the endpoint did not require one; it now answers both with `401 Unauthorized`).

Executed live in the revision pass, after `revise_contract` was published:

- `initialize` and `tools/list`, which returned six tools including `revise_contract`;
- one `revise_contract` submission — a synthetic contract plus one instruction naming a clause explicitly — polled with `get_job` to `completed`, reporting `capability: "revise"` and `outcome: "applied"` with a positive `replaced` and `not_applied` zero;
- `get_artifact` for both artifacts of that job, `revised_docx` and `redline_docx`, each fetched and checked to be a well-formed `.docx`, with the redline checked for real Word tracked-change marks.

Still outstanding:

- **PENDING_AUTH** — `draft_contract` and `compare_contracts`: their success responses, the six draft/compare artifact media types, and the `PARTY_CONFIRMATION_REQUIRED` refusal. Both write to production and neither was called.
- **UNRESOLVED** — a `get_job` response carrying `submitted` (the first poll, 16 seconds in, already read `processing`), the two client configuration files, artifact-URL access control, and rate-limit or retry-hint behavior.
