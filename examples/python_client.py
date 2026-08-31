"""AurCounsel MCP Python example.

Talks to the public AurCounsel MCP endpoint over plain HTTP using only the
Python standard library, so it runs without installing anything:

    python3 examples/python_client.py
    python3 examples/python_client.py <job_id>

What it demonstrates:

    1. initialize            -- protocol handshake, server info
    2. tools/list            -- discover the public tool contract
    3. get_job(job_id)       -- inspect an asynchronous job
    4. get_artifact(job_id)  -- retrieve a completed deliverable

Without an argument it uses the placeholder identifier below, which is
well-formed but belongs to no job, so the run is safe and ends in
JOB_NOT_FOUND. Pass your own job_id to see the populated shapes.

This example never submits work. review_contract, draft_contract and
compare_contracts create real jobs, so they are described in docs/tools.md
rather than executed here.

Transport notes:

  * POST JSON-RPC 2.0 to the endpoint.
  * Accept BOTH application/json and text/event-stream; the server answers
    406 if either is missing.
  * Send your own User-Agent. The edge network in front of the endpoint
    rejects the default Python-urllib user agent with HTTP 403 (Cloudflare
    error 1010, "browser_signature_banned"). Any identifying value works.
  * The response body is a Server-Sent Events frame; the JSON-RPC object is
    on the "data: " line.
  * Tool results arrive as a text content block whose text is itself JSON.

Three failure layers must be handled separately -- see docs/errors.md:

  * transport: a JSON-RPC "error" object;
  * tool execution: result.isError is true, plain-text message;
  * application: result.isError is FALSE and the decoded body has ok=false.

Treat a real job_id as a credential. It is the only handle to the job, it is
not recoverable, and it grants access to that job's artifacts.
"""

import json
import sys
import urllib.error
import urllib.request

AURCOUNSEL_MCP_URL = "https://mcp.clawplus.pro/mcp"
PLACEHOLDER_JOB_ID = "0123456789abcdef"
TIMEOUT_SECONDS = 30
USER_AGENT = "aurcounsel-python-example/0.1.0"


class TransportError(RuntimeError):
    """The endpoint rejected the request before any tool ran."""


class ToolExecutionError(RuntimeError):
    """The tool call itself failed (result.isError)."""


class ApplicationError(RuntimeError):
    """The call succeeded and the body reported ok=false."""

    def __init__(self, payload):
        super().__init__("%s: %s" % (payload.get("error_code"), payload.get("message")))
        self.payload = payload


def rpc(method, params, request_id=1):
    """Send one JSON-RPC request and return the parsed "result" object."""
    body = json.dumps(
        {"jsonrpc": "2.0", "id": request_id, "method": method, "params": params}
    ).encode("utf-8")
    request = urllib.request.Request(
        AURCOUNSEL_MCP_URL,
        data=body,
        method="POST",
        headers={
            "Content-Type": "application/json",
            # Both media types are mandatory; one alone gets HTTP 406.
            "Accept": "application/json, text/event-stream",
            # The default Python-urllib user agent is refused with HTTP 403.
            "User-Agent": USER_AGENT,
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=TIMEOUT_SECONDS) as response:
            raw = response.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        raise TransportError("HTTP %s: %s" % (exc.code, exc.read().decode("utf-8", "replace")))

    message = _decode_sse(raw)
    if "error" in message:
        raise TransportError(json.dumps(message["error"], ensure_ascii=False))
    return message["result"]


def _decode_sse(raw):
    """Pull the JSON-RPC object out of a Server-Sent Events frame."""
    for line in raw.splitlines():
        if line.startswith("data: "):
            return json.loads(line[len("data: ") :])
    # Errors rejected at the transport layer come back as plain JSON.
    return json.loads(raw)


def call_tool(name, arguments):
    """Call a tool and return its decoded JSON body."""
    result = rpc("tools/call", {"name": name, "arguments": arguments})
    text = "".join(
        block.get("text", "") for block in result.get("content", []) if block.get("type") == "text"
    )
    if result.get("isError"):
        raise ToolExecutionError(text)
    payload = json.loads(text)
    if payload.get("ok") is False:
        raise ApplicationError(payload)
    return payload


def main():
    job_id = sys.argv[1] if len(sys.argv) > 1 else PLACEHOLDER_JOB_ID

    print("1. initialize")
    handshake = rpc(
        "initialize",
        {
            "protocolVersion": "2025-06-18",
            "capabilities": {},
            "clientInfo": {"name": "aurcounsel-python-example", "version": "0.1.0"},
        },
    )
    server = handshake["serverInfo"]
    print("   protocol   %s" % handshake["protocolVersion"])
    print("   serverInfo %s %s" % (server["name"], server["version"]))

    print("2. tools/list")
    for tool in rpc("tools/list", {})["tools"]:
        required = tool["inputSchema"].get("required", [])
        print("   %-18s required: %s" % (tool["name"], ", ".join(required) or "(none)"))

    print("3. get_job(%s)" % job_id)
    try:
        job = call_tool("get_job", {"job_id": job_id})
    except ApplicationError as exc:
        print("   application error: %s" % exc)
        print("   (the default identifier is a placeholder; pass a real job_id to go further)")
        return 0
    print("   status          %s" % job.get("status"))
    print("   capability      %s" % job.get("capability"))
    print("   artifacts ready %s"
          % [a["name"] for a in job.get("artifacts") or [] if a.get("ready")])

    if job.get("status") != "completed":
        print("   job is not completed; nothing to retrieve")
        return 0

    ready = [a["name"] for a in job.get("artifacts") or [] if a.get("ready")]
    if not ready:
        print("   no artifact is ready")
        return 0

    name = ready[0]
    print("4. get_artifact(%s, %s)" % (job_id, name))
    artifact = call_tool("get_artifact", {"job_id": job_id, "artifact": name})
    print("   available  %s" % artifact.get("available"))
    print("   media_type %s" % artifact.get("media_type"))
    print("   url        %s" % artifact.get("url"))
    text = artifact.get("text")
    print("   text       %s" % ("null (binary; download the url)" if text is None
                                else "%d characters" % len(text)))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (TransportError, ToolExecutionError) as error:
        print("%s: %s" % (type(error).__name__, error), file=sys.stderr)
        sys.exit(1)
