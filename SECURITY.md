# Security Policy

## Reporting a security issue

Security vulnerabilities should **not** be reported through public GitHub issues.

Please use GitHub's private vulnerability reporting mechanism for this repository.

When writing a report, do not include customer contracts, credentials, job identifiers, artifact URLs, or other sensitive production data unless it is strictly necessary in order to reproduce the issue.

General usage questions and non-security bugs can use the normal public issue channel if and when that channel is enabled for this repository.

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
