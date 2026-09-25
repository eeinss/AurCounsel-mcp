# Error Semantics

AurCounsel MCP distinguishes transport/request errors, job outcomes, and artifact availability. Clients should preserve those distinctions rather than collapse every non-success result into "still processing."

There are **three** distinct failure layers, and they are not interchangeable. All three were captured live.

| Layer | Where it appears | Marker |
|---|---|---|
| 1. Transport / JSON-RPC | HTTP status + a JSON-RPC `error` object | `error.code` is negative |
| 2. Tool execution | `result.isError: true`, message in the text content | `isError: true` |
| 3. Application | `result.isError: false`, JSON body in the text content | `"ok": false` with `error_code` |

The trap is layer 3: an application error arrives as a **successful** MCP call. A client that branches only on `isError` will treat `JOB_NOT_FOUND` as a success.

## 1. Transport / JSON-RPC errors

### Unsupported method

Request `{"jsonrpc":"2.0","id":10,"method":"no/such/method","params":{}}` → HTTP 200, `text/event-stream`:

```json
{"jsonrpc":"2.0","id":10,"error":{"code":-32602,"message":"Invalid request parameters","data":""}}
```

### Malformed JSON

A body that is not valid JSON → **HTTP 400**, content type `application/json` (not SSE):

```json
{"jsonrpc":"2.0","id":"server-error",
 "error":{"code":-32700,
          "message":"Parse error: Expecting property name enclosed in double quotes: line 1 column 3 (char 2)"}}
```

The `message` embeds the parser's own position report, so its exact text varies with the input.

### Missing SSE accept

The endpoint requires the client to accept both content types. Sending `Accept: application/json` alone, or omitting `Accept` entirely, → **HTTP 406**, content type `application/json`:

```json
{"jsonrpc":"2.0","id":"server-error",
 "error":{"code":-32600,
          "message":"Not Acceptable: Client must accept both application/json and text/event-stream"}}
```

### Rejected user agent

The endpoint sits behind an edge network that refuses some clients before the request reaches the MCP server. A POST sent with Python's default `Python-urllib/3.11` user agent returns **HTTP 403** with a Cloudflare error document:

```json
{"title":"Error 1010: Access denied","status":403,
 "detail":"The site owner has blocked access based on your browser's signature.",
 "error_code":1010,"error_name":"browser_signature_banned"}
```

This is not a JSON-RPC error and not an authentication failure — it is emitted by the edge, and the body is not JSON-RPC shaped. Sending any identifying `User-Agent` header cleared it: both `aurcounsel-python-example/0.1.0` and `curl/7.88.1` returned HTTP 200 for the same request.

**Set your own `User-Agent`.** The full set of rejected signatures is not published and was not enumerated. **UNRESOLVED.**

## 2. Tool-execution errors

These carry `isError: true` and a plain-text message rather than a JSON body.

### Missing required argument

Calling `get_job` with `{}` returns `isError: true` and this text:

```text
Error executing tool get_job: 1 validation error for get_jobArguments
job_id
  Field required [type=missing, input_value={}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.12/v/missing
```

Schema violations are reported by the server's validation layer and surface as raw validator text. The wording is not a stable public contract; branch on `isError`, not on this string.

### Unknown tool

Calling a tool name that does not exist returns `isError: true` and:

```text
Unknown tool: no_such_tool_xyz
```

## 3. Application errors

`isError` is `false` and the call is a JSON-RPC success. The text content is a JSON object with `ok: false`.

Shape:

```json
{
  "ok": false,
  "error_code": "<CODE>",
  "message": "<human-readable sentence>",
  "context": { }
}
```

### Public error codes

| `error_code` | Observed | Meaning | `context` |
|---|---|---|---|
| `JOB_NOT_FOUND` | yes | No job exists with that identifier. | `{"upstream_status": 404}` |
| `INVALID_INPUT` | yes | An argument was present but could not be used. | `{"field": "<name>"}`, plus `accepted` for `artifact` |
| `JOB_FAILED` | yes | Appears in `get_job`'s `failure` block, not as a top-level `error_code`. | — |
| `PARTY_CONFIRMATION_REQUIRED` | **no** | Declared by the `review_contract` and `draft_contract` descriptions: an unresolvable `represented_party` is refused and the caller is asked which position the client holds. The one submission made during this pass sent a `represented_party` the server did resolve, so it took the success path and this code was never returned. Provoking it means deliberately submitting an unresolvable party, which was not authorised. **UNRESOLVED.** | UNRESOLVED |

This table lists what was observed plus the one code the live descriptions declare. It is **not** certified as the complete set — the server exposes no enumeration of its error codes.

### Unknown job

```json
{"ok":false,"error_code":"JOB_NOT_FOUND",
 "message":"No LegalOS job with that identifier exists.",
 "context":{"upstream_status":404}}
```

This is what an unrecognised identifier produces. It is **not** `status: "unknown"` — see the distinction in [job-lifecycle.md](job-lifecycle.md).

### Malformed identifier

An identifier that is the wrong shape is rejected before lookup:

```json
{"ok":false,"error_code":"INVALID_INPUT",
 "message":"The request could not be read as a LegalOS submission.",
 "context":{"field":"job_id"}}
```

So `job_id` has two distinct rejection paths inside the tool: malformed → `INVALID_INPUT`, well-formed but unknown → `JOB_NOT_FOUND`. On the public endpoint a job identifier your identity did not submit — including an unknown one — is refused earlier, with HTTP `403 Forbidden` (section 6).

### Unknown artifact name

```json
{"ok":false,"error_code":"INVALID_INPUT",
 "message":"The request could not be read as a LegalOS submission.",
 "context":{"field":"artifact",
            "accepted":["redline","original","revised","revised_docx","memo","review_comments",
                        "draft_html","draft_docx","draft_summary",
                        "compare_redline","compare_memo","compare_synthesis"]}}
```

`context.accepted` is the authoritative artifact vocabulary; [artifacts.md](artifacts.md) reproduces it.

Validation order matters: the artifact name is checked **before** the job is looked up. An unknown job with an invalid artifact name reports the artifact problem. An unknown job with a *valid* artifact name reports `JOB_NOT_FOUND`.

## 4. Job-level outcomes

Public job status vocabulary:

```text
submitted
processing
completed
failed
unknown
```

These states are semantically meaningful and should be surfaced directly.

### Terminal failure

`failed` means the job is terminally unsuccessful.

A failed job is **not** an error at any of the three layers above. The call succeeds, `isError` is `false`, and `ok` is `true`. The failure is reported in the body:

```json
"status": "failed",
"upstream_status": "error",
"failure": { "error_code": "JOB_FAILED" }
```

This is stated by the live `get_job` description: failures are reported "in the body rather than as an HTTP error, so check the status and not just the call."

Client handling:

- stop presenting the job as pending;
- expose the public failure information returned by AurCounsel;
- do not treat unavailable artifacts as "not ready yet";
- do not deliver partial/generated internal outputs as completed artifacts.

> Note that `get_artifact` on a failed job returns a `note` telling the caller to keep polling. That advice does not apply to a terminal job. See the caution in [artifacts.md](artifacts.md).

### Unknown status

`unknown` is a `get_job` **result value**, not an error. It means the engine reported a state the server does not map; the raw value is in `upstream_status` and `status_recognised` is `false`. It is not equivalent to `submitted` or `processing`, and it is not what an unrecognised job identifier returns.

Its live behavior was not observed; the description above is the server's own. **UNRESOLVED.**

## 5. Artifact-level errors

Artifact retrieval can fail or return unavailable even when the job object itself can be resolved.

The client should first inspect the parent job state:

```text
if job.status == completed:
    handle artifact availability according to artifact contract
elif job.status == failed:
    explain terminal failure
else:
    do not claim a completed deliverable exists
```

This prevents a known UX ambiguity in which an unavailable artifact can sound merely premature even though the job has already failed.

## 6. Authentication and authorization errors

Every MCP request must carry `Authorization: Bearer <AURCOUNSEL_MCP_TOKEN>`. These refusals happen before any MCP method runs; the body is plain text, not a JSON-RPC envelope.

| HTTP status | Meaning |
| --- | --- |
| `401 Unauthorized` | Missing or invalid bearer token. The response carries `WWW-Authenticate: Bearer`. |
| `403 Forbidden` | Authenticated, but the identity does not have access to the requested job/artifact. |

Jobs and artifacts are scoped to the authenticated identity. A job or artifact identifier alone does not grant access.

## 7. Rate limits and transient errors

**UNRESOLVED.** No rate-limit headers, `retry_after` field, or throttling response was observed. The capture was small and deliberately read-only; absence here is not evidence that no limit exists.

## 8. Recommended client messaging

| Situation | Recommended meaning |
|---|---|
| `submitted` | Request accepted; work has not completed. |
| `processing` | Work is in progress. |
| `completed` | Job succeeded; retrieve completed deliverables. |
| `failed` | Job ended unsuccessfully; no completed deliverable should be inferred. |
| `unknown` | The engine reported a state the server could not map; read `upstream_status`. |
| `JOB_NOT_FOUND` | No such job. Do not retry with the same identifier. |
| artifact unavailable + failed job | Artifact is unavailable because the job failed. |

## 9. Retry guidance

Do not blindly retry every error.

- `submitted` / `processing`: checking status again is expected.
- `completed`: stop status polling.
- `failed`: stop status polling; submit a new job only when appropriate for the calling application.
- `unknown`: read `upstream_status` and surface it; do not treat it as progress.
- `JOB_NOT_FOUND`: the identifier is wrong or the job never existed. Retrying will not change the answer.
- request validation error (layer 2 or `INVALID_INPUT`): correct the request before retrying.
- HTTP 406: add `Accept: application/json, text/event-stream`. Retrying unchanged will always fail.
