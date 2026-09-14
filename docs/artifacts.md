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

Artifacts are retrieved through `get_artifact` using the `job_id` and the artifact `name` as reported in `get_job`'s `artifacts[]` list.

## What counts as a completed deliverable

A completed deliverable is an artifact that the public interface makes available for a job that has successfully reached `completed`, subject to the exact artifact contract.

A generated file or intermediate object that may exist internally does **not** become a public completed deliverable merely because some processing occurred.

For a `failed` job:

> Partial/generated internal artifacts are not considered completed deliverables.

Clients should not expose them as final results.

## Artifact types

The accepted vocabulary is not inferred: it is returned verbatim by the live server in `context.accepted` when `get_artifact` is called with an unrecognised artifact name. Which names are valid for a given job depends on that job's `capability`:

```text
review:   redline, original, revised, revised_docx, memo, review_comments
draft:    draft_html, draft_docx, draft_summary
compare:  compare_redline, compare_memo, compare_synthesis
revise:   revised_docx, redline_docx
```

Read `context.accepted` from the live server rather than counting the list above.

The `media_type` and `inline_text_available` columns below are verbatim from the `artifacts[]` list of the completed `get_job` reading on the synthetic contract submitted during the review pass; the two `revise` rows are from the completed revision job and the artifacts it served; the `draft` and `compare` rows are from the live `get_artifact` description, since no draft or compare job was observed.

| Artifact | Produced by | Meaning (from the live description) | Media type | Inline text |
|---|---|---|---|---|
| `redline` | review | Tracked-change view of the changes | `text/html` | yes |
| `original` | review | The submitted contract | `text/html` | yes |
| `revised` | review | The revised contract | `text/html` | yes |
| `revised_docx` | review, revise | The revised contract to deliver | `application/vnd.openxmlformats-officedocument.wordprocessingml.document` | **no** |
| `memo` | review | The opinion document | `text/html` | yes |
| `review_comments` | review | The review opinion the UI shows the lawyer | `text/markdown` | yes |
| `redline_docx` | revise | The revised contract carrying the changes as Word revision marks | `application/vnd.openxmlformats-officedocument.wordprocessingml.document` | **no** |
| `draft_html` | draft | The drafted contract | UNRESOLVED | UNRESOLVED |
| `draft_docx` | draft | The same contract to deliver | UNRESOLVED | UNRESOLVED |
| `draft_summary` | draft | Summary of the draft | UNRESOLVED | UNRESOLVED |
| `compare_redline` | compare | What changed between the two versions | UNRESOLVED | UNRESOLVED |
| `compare_memo` | compare | Comparison opinion document | UNRESOLVED | UNRESOLVED |
| `compare_synthesis` | compare | Comparison synthesis | UNRESOLVED | UNRESOLVED |

The six `UNRESOLVED` media types require a `draft` or `compare` job to observe. Neither capability has been submitted, so they remain unobserved. See the PENDING_AUTH notes in [tools.md](tools.md).

### Revision artifacts

A `revise` job serves two artifacts, and they are not interchangeable:

- `revised_docx` — the revised contract as a clean Word document. The new text is in place and the document carries no revision marks.
- `redline_docx` — the same result as a Word document carrying the changes as tracked revision marks, so that the change can be read, and accepted or rejected, in Word.

Both are binary, and both are returned as a URL only with `text: null`, like any other `.docx` artifact.

**Do not confuse `redline_docx` with `redline`.** A review's `redline` is an HTML view of the changes. `redline_docx` is a Word document with the revision marks inside it. Different capability, different artifact, different format.

## `get_artifact` response

> **The three response bodies in this section are sanitized examples.** Their keys, nesting, and value types are the verified live response shape — the field table below is the same shape, and none of it is guessed. The identifiers, URLs, and any value that would carry document content are replaced with placeholders. No body below is presented as the verbatim capture of a particular job, and no submitted document content is reproduced anywhere in this repository.

The call returns `isError: false` with a single text content block containing a JSON object.

| Field | Type | Present when | Meaning |
|---|---|---|---|
| `ok` | boolean | always | `true` when the job resolved, including when the artifact is unavailable. |
| `job_id` | string | always | Echo of the request. |
| `artifact` | string | always | Echo of the requested artifact name. |
| `capability` | string | always | `review`, `draft`, `compare`, or `revise`. |
| `available` | boolean | always | Whether the artifact has been written. |
| `url` | string | always | `https://mcp.clawplus.pro/artifact/<job_id>/<artifact>` |
| `media_type` | string | when available | MIME type of the artifact. |
| `text` | string \| null | when available | Inline content for text artifacts; `null` for binary artifacts. |
| `status` | string | when unavailable | The parent job's status. |
| `note` | string | binary or unavailable | Server-supplied explanatory text. See the caution below. |

### Available text artifact

Request:

```json
{"jsonrpc":"2.0","id":1,"method":"tools/call",
 "params":{"name":"get_artifact","arguments":{"job_id":"<JOB_ID>","artifact":"review_comments"}}}
```

Response — a sanitized example in the verified live shape. The call succeeds and `text` carries the review opinion inline; the opinion is the submitted document's content, so it is shown here as a placeholder:

```json
{
  "ok": true,
  "job_id": "<JOB_ID>",
  "artifact": "review_comments",
  "capability": "review",
  "available": true,
  "url": "https://mcp.clawplus.pro/artifact/<JOB_ID>/review_comments",
  "media_type": "text/markdown",
  "text": "<omitted — markdown review opinion; this field carries the submitted document's content>"
}
```

The shape was confirmed on all six review artifacts. The five text artifacts (`redline`, `original`, `revised`, `memo`, `review_comments`) return a non-null `text`.

### Binary artifact

A `.docx` artifact is returned as a URL only, with `text: null` (sanitized example, same shape):

```json
{
  "ok": true,
  "job_id": "<JOB_ID>",
  "artifact": "revised_docx",
  "capability": "review",
  "available": true,
  "url": "https://mcp.clawplus.pro/artifact/<JOB_ID>/revised_docx",
  "media_type": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
  "text": null,
  "note": "Binary artifact — download it from the URL. Present the credential this call was made with; it is the same server."
}
```

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

### Observed failed-job response

Requesting `memo` from a terminally failed job returns (sanitized example, same shape):

```json
{
  "ok": true,
  "job_id": "<FAILED_JOB_ID>",
  "artifact": "memo",
  "capability": "review",
  "available": false,
  "status": "failed",
  "url": "https://mcp.clawplus.pro/artifact/<FAILED_JOB_ID>/memo",
  "note": "This artifact has not been written yet. Poll get_job and read `artifacts[].ready`."
}
```

> **Caution — the `note` field is not authoritative about job state.** The machine-readable fields are correct and sufficient: `available` is `false` and `status` is `failed`, which is terminal. The accompanying `note`, however, says "has not been written **yet**" and tells the caller to keep polling. That advice is wrong for a terminal job — no amount of polling will make this artifact appear.
>
> Clients must decide on `status`, not on `note`. Do not relay the `note` text to an end user for a job whose status is `failed`.
>
> This is recorded as observed live behavior. Changing the server's wording is a product decision and is out of scope for this repository.

## Missing artifact and unknown job

- **Unrecognised artifact name** — an `INVALID_INPUT` application error whose `context.accepted` lists the valid names. See [errors.md](errors.md).
- **Unknown job identifier** — a `JOB_NOT_FOUND` application error. The artifact name is validated first: an unknown job combined with an invalid artifact name reports the artifact problem, not the job problem.
- **Artifact requested before it is ready on a live job** — the live description states this returns `available: false` rather than an error. **UNRESOLVED.** `get_artifact` was never called on a job that was still `processing`. What *was* observed is the neighbouring fact, from `get_job`: on a live `processing` job the `artifacts` array is already fully populated, with every `ready` set to `false` (see [job-lifecycle.md](job-lifecycle.md)). That is the field to branch on. What `get_artifact` itself returns in that window — and what its `note` says — is not established.

## Integrity and completeness

Clients should consume the artifact exactly as returned by the public contract and should not assume that undocumented internal artifacts exist.

The live responses expose no checksum, no byte length, no expiry, and no pagination. Structured sections are not exposed as fields; text artifacts arrive as a single `text` string.

> **UNRESOLVED — artifact URL access.** Every response carries an artifact `url`, and the binary-artifact `note` says to "present the credential this call was made with." The MCP endpoint itself accepted requests with no credential at all (see [quickstart.md](quickstart.md)). What, if anything, guards `https://mcp.clawplus.pro/artifact/...` was not tested: fetching those URLs was outside the scope of this verification pass. This repository therefore makes no claim in either direction — not that those URLs are public, not that they require authentication, and not that they are permanent.
>
> **Because it is unresolved, handle it conservatively.** Treat the `job_id`, and any artifact reference or URL returned alongside it, as sensitive. Do not publish them, paste them into shared logs or issue trackers, or pass them to a third party. The supported way to read a deliverable is `get_job` to confirm the job is `completed`, then `get_artifact` over the MCP endpoint — not by fetching the `url` out of band.
