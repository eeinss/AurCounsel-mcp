# Changelog

All notable changes to the public AurCounsel MCP interface documentation will be recorded here.

The format is inspired by Keep a Changelog. Version numbers in this repository describe the **public documentation/interface contract**, not private backend release identifiers.

## [0.1.0] - Unreleased

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

### Pending verification before publication

- Exact live MCP tool schemas.
- Exact response shapes.
- Exact job response vocabulary/fields.
- Exact artifact types and retrieval schema.
- Exact authentication requirements.
- Exact public error envelope/codes.
- Executable examples tested against production.
- Approved security-reporting channel.
- Approved repository license.

[0.1.0]: https://github.com/REPLACE_WITH_ORG/aurcounsel-mcp/releases/tag/v0.1.0
