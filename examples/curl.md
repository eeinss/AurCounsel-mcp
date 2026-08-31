# curl examples

AurCounsel MCP endpoint:

```text
https://mcp.clawplus.pro/mcp
```

## Important

MCP transport framing, headers, session behavior, and request payloads must match the live production transport. A plain `curl` invocation that only proves HTTP reachability is **not** the same as a verified MCP tool call.

Every command on this page was executed against the public production endpoint, and the responses below are the responses those commands returned.

## Transport requirements

The endpoint speaks JSON-RPC 2.0 over HTTP POST and answers with a Server-Sent Events frame.

- `Content-Type: application/json`
- `Accept: application/json, text/event-stream` — **both** media types are required. Sending only one, or omitting `Accept`, returns HTTP 406.
- Responses arrive as `text/event-stream`: an `event: message` line followed by a `data: {...}` line carrying the JSON-RPC object.
- No session header is used. Responses carry no `Mcp-Session-Id`, and none needs to be sent back.

To turn a response into plain JSON, pipe the response through this filter, which strips the SSE prefix:

```text
sed -n 's/^data: //p'
```

It is used that way in section 2 below.

### Job identifiers in these examples

The job identifier below is the obvious placeholder `0123456789abcdef`. It is well-formed but belongs to no job, so every command on this page is safe to run verbatim and will answer `JOB_NOT_FOUND`. Substitute your own `job_id` to see the populated shapes documented in [../docs/tools.md](../docs/tools.md) and [../docs/artifacts.md](../docs/artifacts.md).

Treat a real `job_id` as a credential: it is the only handle to that job, it is not recoverable, and it grants artifact access.

## 1. Connectivity / protocol negotiation

```bash
curl -sS -X POST https://mcp.clawplus.pro/mcp \
  -H 'Content-Type: application/json' \
  -H 'Accept: application/json, text/event-stream' \
  -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-06-18","capabilities":{},"clientInfo":{"name":"curl","version":"0"}}}'
```

HTTP 200, `text/event-stream`:

```text
event: message
data: {"jsonrpc":"2.0","id":1,"result":{"protocolVersion":"2025-06-18","capabilities":{"experimental":{},"prompts":{"listChanged":false},"resources":{"subscribe":false,"listChanged":false},"tools":{"listChanged":false}},"serverInfo":{"name":"legalos","version":"1.27.0"},"instructions":"LegalOS contract capabilities. ..."}}
```

`instructions` is elided above for width; it is reproduced in full in [../docs/tools.md](../docs/tools.md).

> `legalos` is the **server identifier** returned on the wire by the live deployment — a compatibility identifier for clients that key off `serverInfo.name` — not the product name. The product is **AurCounsel**. Server-emitted strings, including the `instructions` text above, are reproduced here exactly as received. See [../docs/tools.md](../docs/tools.md).

## 2. Tool discovery

```bash
curl -sS -X POST https://mcp.clawplus.pro/mcp \
  -H 'Content-Type: application/json' \
  -H 'Accept: application/json, text/event-stream' \
  -d '{"jsonrpc":"2.0","id":2,"method":"tools/list","params":{}}'
```

Returns the five tools with their full descriptions and JSON input schemas. To list just the names:

```bash
curl -sS -X POST https://mcp.clawplus.pro/mcp \
  -H 'Content-Type: application/json' \
  -H 'Accept: application/json, text/event-stream' \
  -d '{"jsonrpc":"2.0","id":2,"method":"tools/list","params":{}}' \
  | sed -n 's/^data: //p' \
  | python3 -c 'import json,sys; print("\n".join(t["name"] for t in json.load(sys.stdin)["result"]["tools"]))'
```

Output:

```text
review_contract
draft_contract
compare_contracts
get_job
get_artifact
```

## 3. Submit `review_contract`

**Deliberately not executable as written.** Sending this command creates a job and writes a row in the production system. One `review_contract` submission was authorised during this pass and its request and response are recorded in [../docs/tools.md](../docs/tools.md) — the arguments below carry the same field names and the same values, except that the real call sent a 50 072-character base64 payload where this shows `<BASE64_DOCX>`. The command is left with that placeholder on purpose, so that nothing on this page can be pasted into a terminal and silently create a job. Substitute a real payload only when you intend to submit.

```bash
# NOT EXECUTED — creates a production job.
# file_b64 is the base64 of a .docx file; file_name and file_b64 are required.
curl -sS -X POST https://mcp.clawplus.pro/mcp \
  -H 'Content-Type: application/json' \
  -H 'Accept: application/json, text/event-stream' \
  -d '{"jsonrpc":"2.0","id":3,"method":"tools/call","params":{"name":"review_contract","arguments":{"file_name":"agreement.docx","file_b64":"<BASE64_DOCX>","requested_jurisdiction":"taiwan","represented_party":"Party A"}}}'
```

## 4. Check `get_job`

```bash
curl -sS -X POST https://mcp.clawplus.pro/mcp \
  -H 'Content-Type: application/json' \
  -H 'Accept: application/json, text/event-stream' \
  -d '{"jsonrpc":"2.0","id":4,"method":"tools/call","params":{"name":"get_job","arguments":{"job_id":"0123456789abcdef"}}}'
```

HTTP 200. The placeholder identifier resolves to no job, so the tool call succeeds and reports an application error in its body:

```text
event: message
data: {"jsonrpc":"2.0","id":4,"result":{"content":[{"type":"text","text":"{\n  \"ok\": false,\n  \"error_code\": \"JOB_NOT_FOUND\",\n  \"message\": \"No LegalOS job with that identifier exists.\",\n  \"context\": {\n    \"upstream_status\": 404\n  }\n}"}],"isError":false}}
```

Note `isError` is `false`. See [../docs/errors.md](../docs/errors.md) for why that matters. With a real `job_id` the same command returns the populated job object documented in [../docs/tools.md](../docs/tools.md).

## 5. Retrieve `get_artifact`

```bash
curl -sS -X POST https://mcp.clawplus.pro/mcp \
  -H 'Content-Type: application/json' \
  -H 'Accept: application/json, text/event-stream' \
  -d '{"jsonrpc":"2.0","id":5,"method":"tools/call","params":{"name":"get_artifact","arguments":{"job_id":"0123456789abcdef","artifact":"memo"}}}'
```

HTTP 200, same `JOB_NOT_FOUND` body as above:

```text
event: message
data: {"jsonrpc":"2.0","id":5,"result":{"content":[{"type":"text","text":"{\n  \"ok\": false,\n  \"error_code\": \"JOB_NOT_FOUND\",\n  \"message\": \"No LegalOS job with that identifier exists.\",\n  \"context\": {\n    \"upstream_status\": 404\n  }\n}"}],"isError":false}}
```

The argument is named `artifact`, not `artifact_type`, and it must be one of the twelve values listed in [../docs/artifacts.md](../docs/artifacts.md).

## 6. Diagnosing a rejected request

Omit the SSE media type and the endpoint refuses before any tool runs:

```bash
curl -sS -i -X POST https://mcp.clawplus.pro/mcp \
  -H 'Content-Type: application/json' \
  -H 'Accept: application/json' \
  -d '{"jsonrpc":"2.0","id":6,"method":"tools/list","params":{}}'
```

HTTP 406, `application/json`:

```json
{"jsonrpc":"2.0","id":"server-error","error":{"code":-32600,"message":"Not Acceptable: Client must accept both application/json and text/event-stream"}}
```

If your client hangs instead of returning, check that you are issuing a POST. A GET to the same URL opens a long-lived SSE channel and emits periodic `: ping` comments rather than answering a request.

## Sanitization rules

Public curl examples must not contain:

- real credentials or bearer tokens;
- private contract content;
- internal hostnames, ports, or filesystem paths;
- production database identifiers;
- private fixture names;
- release/reviewer/executor traces;
- real job identifiers.
