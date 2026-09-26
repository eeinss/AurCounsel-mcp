# Changelog

All notable changes to the public AurCounsel MCP interface documentation will be recorded here.

The format is inspired by Keep a Changelog. Version numbers in this repository describe the **public documentation/interface contract**, not private backend release identifiers.

## [0.1.0] - Unreleased

### Added

- `legal_research` tool (Legal Research): submit a legal question, poll `get_job`, read `research_markdown` or `get_artifact(job_id, "research")`. Documented in README, quickstart, tools, job lifecycle and curl examples.

### Changed

- `review_contract`: `represented_party` is required. A call without it is refused with `INVALID_INPUT` and a readable message before anything is sent; there is no automatic party detection. Docs and schema capture updated to the live server.
- Authentication is required: every MCP request, including artifact downloads, must carry `Authorization: Bearer <AURCOUNSEL_MCP_TOKEN>`. Missing or invalid token: `401 Unauthorized`.
- Jobs and artifacts are scoped to the authenticated identity; reading another identity's job or artifact returns `403 Forbidden`. A job or artifact identifier alone does not grant access.
- README, quickstart, curl, Python and client-configuration examples updated to send the bearer header from `$AURCOUNSEL_MCP_TOKEN`; errors and artifacts pages document `401` / `403`.

### Added

- Initial public repository information architecture.
- Public AurCounsel MCP endpoint documentation.
- Documentation for the primary tools:
  - `review_contract`
  - `draft_contract`
  - `compare_contracts`
  - `get_job`
  - `get_artifact`
- Public asynchronous job lifecycle with:
  - `submitted`
  - `processing`
  - `completed`
  - `failed`
  - `unknown`
- Explicit terminal-failure semantics: partial/generated internal artifacts are not completed deliverables.
- Quickstart, architecture, artifact, error, security, and example documentation.
- Machine-truth verification markers for live schemas, response shapes, artifact vocabulary, authentication, and executable examples.
- MIT license for the contents of this repository.
- Security policy naming GitHub private vulnerability reporting as the channel for vulnerability reports.

### Verified against the live endpoint

- Exact descriptions and JSON input schemas for all five tools, from a live `tools/list`.
- Transport contract: JSON-RPC 2.0 over POST, protocol version `2025-06-18`, dual `Accept` requirement, SSE response framing, no session header, and the edge network's rejection of some user agents.
- `get_job` response shape, canonical status field, and the `completed`, `processing`, and `failed` bodies.
- One authorised `review_contract` submission of a synthetic contract, followed from submission to `completed`: the success-response shape, the `job_id` field path, ten `get_job` reads, and the observed `progress` stages.
- The twelve-value artifact vocabulary, taken verbatim from the server's own `context.accepted`.
- `get_artifact` response shape for available text artifacts, binary artifacts, and a terminally failed job. The bodies published in [artifacts.md](docs/artifacts.md) are sanitized examples in that verified shape — identifiers, URLs, and document content are placeholders — not verbatim captures.
- Error envelopes at all three layers: transport, tool execution, and application.
- Authentication state: none enforced at the MCP endpoint.
- `serverInfo.name` is `legalos` on the live deployment. That is the server identifier returned on the wire — a compatibility identifier for clients that key off `serverInfo.name` — and it is reproduced here unchanged. The product documented by this repository is AurCounsel; server-emitted strings are never rewritten, and this repository's own prose says AurCounsel throughout.
- `examples/curl.md` and `examples/python_client.py`, both executed as written.

### Pending verification before publication

- **PENDING_AUTH** — `draft_contract` and `compare_contracts` write to production and were never called: their success-response shapes, the six draft/compare artifact media types, and the `PARTY_CONFIRMATION_REQUIRED` refusal. The `review_contract` submission that was authorised does not establish these by analogy.
- **UNRESOLVED** — a `get_job` reading of `submitted` (the status appeared only in the submission response), `unknown` status behavior, failure detail beyond `JOB_FAILED`, the full progress-stage vocabulary, the transition set, rate limits and retry hints, artifact-URL access control, and the two client configuration file formats.
- The `get_artifact` response bodies in [artifacts.md](docs/artifacts.md) are sanitized examples in the verified live shape, not verbatim captures. The `failed` `get_job` body uses a placeholder identifier for the same reason.
