# Quickstart

This guide is designed for an engineer who has never used AurCounsel before. The goal is to connect an MCP client, submit one contract operation, observe the job lifecycle, and retrieve a completed artifact.

## 1. Endpoint

AurCounsel MCP is available at:

```text
https://mcp.clawplus.pro/mcp
```

The production endpoint may retain the `clawplus.pro` domain while the product brand is **AurCounsel**.

## 2. Prerequisites

You need:

- an MCP-compatible client;
- network access to the public endpoint;
- a contract input accepted by the selected AurCounsel tool;
- any authentication material required by the live service, if authentication is enabled for your access path.

> **MACHINE TRUTH REQUIRED — authentication:** Executor must confirm whether the current public endpoint requires authentication, and if so, the exact transport/header/token mechanism. Do not infer or document authentication from private deployment configuration.

## 3. Configure your MCP client

Use the public endpoint as the MCP server URL.

Example client files are available in:

- [`../examples/claude-desktop.json`](../examples/claude-desktop.json)
- [`../examples/cursor.json`](../examples/cursor.json)

These files intentionally isolate endpoint configuration from private implementation details.

> **MACHINE TRUTH REQUIRED — client config syntax:** MCP client configuration formats change between client versions. Executor should verify the exact working configuration against the currently supported production transport before this repo is published.

## 4. Discover the tools

After connecting, confirm the server exposes the expected primary tools:

```text
review_contract
draft_contract
compare_contracts
get_job
get_artifact
```

The canonical schemas are whatever the live MCP server returns through tool discovery. The prose documentation in this repo must be regenerated or corrected whenever it diverges from that machine-readable contract.

## 5. Submit a job

Choose one operation. For example, a contract review follows this conceptual sequence:

```text
review_contract(<live input schema>)
```

A successful submission returns enough information to identify the asynchronous job, including a `job_id`.

> **MACHINE TRUTH REQUIRED — submission response:** Executor must provide the exact response shape and identify which field contains the canonical `job_id`.

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

The client should continue checking only while the job is non-terminal. `completed` and `failed` are terminal outcomes. `unknown` means the requested job cannot currently be resolved as a known job and must not be treated as an in-progress state.

See [job-lifecycle.md](job-lifecycle.md) for full semantics.

## 7. Retrieve artifacts

Once a job reaches `completed`, request a completed deliverable with:

```text
get_artifact(<live artifact lookup schema>)
```

> **MACHINE TRUTH REQUIRED — artifact lookup:** Executor must provide the exact `get_artifact` input schema, artifact identifiers/types, response shape, content encoding, and behavior for missing artifacts.

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

## Before publication: executable quickstart gate

This guide should be considered publishable only after Executor supplies and Reviewer verifies:

- one exact, live `tools/list` capture;
- one successful `review_contract` request;
- the exact submission response;
- one `get_job` response for a non-terminal state;
- one `get_job` response for `completed`;
- one `get_artifact` request and successful response;
- one terminal `failed` example demonstrating that unavailable artifacts are not described as merely pending;
- current authentication requirements, if any.
