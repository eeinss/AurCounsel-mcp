# Error Semantics

AurCounsel MCP distinguishes transport/request errors, job outcomes, and artifact availability. Clients should preserve those distinctions rather than collapse every non-success result into "still processing."

## 1. Request-level errors

A request-level error occurs when a tool call cannot be accepted or interpreted according to the public tool contract.

Examples may include invalid input, missing required fields, or invalid identifiers — but the exact error codes and shapes must come from production.

**MACHINE TRUTH REQUIRED:** Executor must supply the exact public error envelope, codes, messages, and relevant HTTP/MCP transport behavior.

## 2. Job-level outcomes

Public job status vocabulary:

```text
submitted
processing
completed
failed
unknown
```

These states are semantically meaningful and should be surfaced directly.

### Terminal failure

`failed` means the job is terminally unsuccessful.

Client handling:

- stop presenting the job as pending;
- expose the public failure information returned by AurCounsel;
- do not treat unavailable artifacts as "not ready yet";
- do not deliver partial/generated internal outputs as completed artifacts.

### Unknown job

`unknown` means the requested job cannot currently be resolved as a known job. It is not equivalent to `submitted` or `processing`.

**MACHINE TRUTH REQUIRED:** Verify whether `unknown` is represented as a normal `get_job` payload, a tool error, or both depending on input class.

## 3. Artifact-level errors

Artifact retrieval can fail or return unavailable even when the job object itself can be resolved.

The client should first inspect the parent job state:

```text
if job.status == completed:
    handle artifact availability according to artifact contract
elif job.status == failed:
    explain terminal failure
else:
    do not claim a completed deliverable exists
```

This prevents a known UX ambiguity in which an unavailable artifact can sound merely premature even though the job has already failed.

## 4. Recommended client messaging

| Situation | Recommended meaning |
|---|---|
| `submitted` | Request accepted; work has not completed. |
| `processing` | Work is in progress. |
| `completed` | Job succeeded; retrieve completed deliverables. |
| `failed` | Job ended unsuccessfully; no completed deliverable should be inferred. |
| `unknown` | The requested job cannot be resolved as a known job. |
| artifact unavailable + failed job | Artifact is unavailable because the job failed. |

## 5. Retry guidance

Do not blindly retry every error.

- `submitted` / `processing`: checking status again is expected.
- `completed`: stop status polling.
- `failed`: stop status polling as though completion were still expected; submit a new job only when appropriate for the calling application.
- `unknown`: verify the identifier and follow the exact live error contract.
- request validation error: correct the request before retrying.

> **MACHINE TRUTH REQUIRED:** Add documented rate-limit, retry-after, transient-error, timeout, and idempotency behavior only if exposed and verified by the live public service.
