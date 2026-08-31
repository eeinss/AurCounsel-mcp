# curl examples

AurCounsel MCP endpoint:

```text
https://mcp.clawplus.pro/mcp
```

## Important

MCP transport framing, headers, session behavior, and request payloads must match the live production transport. A plain `curl` invocation that only proves HTTP reachability is **not** the same as a verified MCP tool call.

For that reason, this V0.1 draft does not invent JSON-RPC payloads or headers.

## Executor verification required

Before publication, replace the placeholders below with commands that were actually executed against the public production endpoint.

### 1. Connectivity / protocol negotiation

```bash
# MACHINE TRUTH REQUIRED
# Insert verified curl command and sanitized response.
```

### 2. Tool discovery

```bash
# MACHINE TRUTH REQUIRED
# Insert verified command that retrieves the live tool list/schema.
```

### 3. Submit `review_contract`

```bash
# MACHINE TRUTH REQUIRED
# Insert exact verified request using the live schema.
```

Expected result: a successful response containing the canonical job identifier.

### 4. Check `get_job`

```bash
# MACHINE TRUTH REQUIRED
# Insert exact verified request.
```

### 5. Retrieve `get_artifact`

```bash
# MACHINE TRUTH REQUIRED
# Insert exact verified request for a completed job.
```

## Sanitization rules

Public curl examples must not contain:

- real credentials or bearer tokens;
- private contract content;
- internal hostnames, ports, or filesystem paths;
- production database identifiers;
- private fixture names;
- release/reviewer/executor traces.
