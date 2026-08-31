# Security Policy

## Reporting a security issue

Please do **not** publish sensitive security reports, credentials, confidential contracts, production data, or exploit details in a public GitHub issue.

**MACHINE TRUTH / OWNER INPUT REQUIRED:** Before publication, replace this paragraph with the approved private security-reporting channel (for example, a dedicated security email address or GitHub private vulnerability reporting workflow).

Until an official reporting channel is inserted, this repository should remain unpublished.

## Sensitive information

Do not include any of the following in issues, pull requests, examples, logs, screenshots, or documentation contributions:

- API keys, tokens, cookies, credentials, or secrets;
- confidential or personal contracts;
- private uploaded fixtures;
- production database contents or schema snapshots;
- private legal corpus data;
- internal prompts;
- internal model endpoints;
- private infrastructure addresses, ports, or topology;
- tunnel configuration;
- internal release, reviewer, or executor records.

## Public examples

Examples in this repository must use synthetic or clearly non-confidential content. Before merging an example captured from production, verify that it contains no private contract text, user data, internal identifiers, or implementation details.

## Scope of this repository

`aurcounsel-mcp` documents the public MCP interface. It is not the source repository for the AurCounsel backend. Reports about accidental disclosure of private implementation details in this repository should be treated as security-sensitive.

## Supported versions

The public documentation begins at version `0.1.x`. A formal security support/version policy will be added when the public interface versioning policy is finalized.
