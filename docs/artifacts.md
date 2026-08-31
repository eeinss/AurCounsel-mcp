# Artifacts

Artifacts are completed deliverables exposed by AurCounsel after successful contract work.

## Retrieval model

The public flow is:

```text
submit contract operation
-> receive job_id
-> get_job(job_id)
-> wait for completed
-> get_artifact(...)
```

Artifacts are retrieved through `get_artifact` using the identifiers and/or artifact-type fields defined by the live MCP schema.

## What counts as a completed deliverable

A completed deliverable is an artifact that the public interface makes available for a job that has successfully reached `completed`, subject to the exact artifact contract.

A generated file or intermediate object that may exist internally does **not** become a public completed deliverable merely because some processing occurred.

For a `failed` job:

> Partial/generated internal artifacts are not considered completed deliverables.

Clients should not expose them as final results.

## Artifact types

**MACHINE TRUTH REQUIRED**

Executor must provide the exact live artifact-type vocabulary. Do not infer artifact names from internal file names, private database columns, release fixtures, or implementation code.

Replace this section with a table after verification:

| Artifact type | Produced by | Meaning | Content/encoding | Availability rules |
|---|---|---|---|---|
| `<LIVE_VALUE>` | `<tool>` | `<verified description>` | `<verified>` | `<verified>` |

## `get_artifact` response

**MACHINE TRUTH REQUIRED**

Document the exact production response shape, including only public fields. Verify:

- artifact ID or type field;
- job association;
- availability field, if any;
- content payload or retrieval location;
- MIME/content type if exposed;
- filename if exposed;
- metadata if exposed;
- error details for missing/unavailable artifacts.

## Failed-job semantics

If `get_artifact` or `get_job` reports an artifact as unavailable for a job already in `failed`, client text should communicate terminal failure.

Recommended semantic form:

```text
This artifact is unavailable because the job failed.
```

Avoid wording equivalent to:

```text
This artifact is not available yet.
```

when the job is already terminal.

## Integrity and completeness

Clients should consume the artifact exactly as returned by the public contract and should not assume that undocumented internal artifacts exist.

> **MACHINE TRUTH REQUIRED:** If production exposes checksums, byte lengths, structured sections, multiple downloadable formats, expiry semantics, or pagination, document those fields here only after live verification.
