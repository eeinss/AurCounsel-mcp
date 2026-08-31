# Job Lifecycle

AurCounsel contract operations are modeled as asynchronous jobs. Clients submit work, receive a job identifier, inspect the job until it reaches a terminal state, and retrieve deliverables only after successful completion.

## Public state model

The public status vocabulary is:

```text
submitted
processing
completed
failed
unknown
```

### `submitted`

AurCounsel has accepted the job into the public workflow, but processing is not yet reported as active or complete.

Client behavior:

- preserve the `job_id`;
- do not request or present a final deliverable as completed;
- check the job again according to the client's retry policy.

### `processing`

AurCounsel is processing the job.

Client behavior:

- continue to treat the job as non-terminal;
- do not present intermediate or unavailable artifacts as final output;
- check the job again according to the client's retry policy.

### `completed`

The job completed successfully.

Client behavior:

- treat the job as terminal success;
- retrieve the required completed deliverable(s) with `get_artifact` according to the live artifact schema;
- handle an individually unavailable artifact as an artifact-level condition, not by rewriting the job status.

### `failed`

The job terminated without a successful completed result.

Client behavior:

- stop polling as if progress were still expected;
- surface the failure semantics returned by the public API;
- do not treat partial/generated internal artifacts as completed deliverables;
- do not convert `available: false` into a message implying that the artifact is merely "not ready yet" if the parent job is already terminal failed.

This distinction is intentional and is part of the public contract.

### `unknown`

The requested job cannot currently be resolved as a known AurCounsel job.

Client behavior:

- do not interpret `unknown` as queued, pending, or processing;
- verify the identifier and request context;
- follow the exact live error semantics once Executor has captured them.

## State diagram

```text
                 ┌──────────────┐
                 │  submitted   │
                 └──────┬───────┘
                        │
                        v
                 ┌──────────────┐
                 │  processing  │
                 └──────┬───────┘
                        │
              ┌─────────┴─────────┐
              v                   v
       ┌──────────────┐     ┌──────────────┐
       │  completed   │     │    failed    │
       └──────────────┘     └──────────────┘
          terminal             terminal

unknown = requested job cannot be resolved as a known job
```

> **MACHINE TRUTH REQUIRED:** Executor should verify whether production permits direct transitions such as `submitted -> completed`, `submitted -> failed`, or other state observations. The public docs should describe observed semantics rather than infer unexposed internal transitions.

## Polling guidance

AurCounsel does not require a specific client polling interval in this draft. Clients should avoid tight loops and should use a reasonable retry/backoff strategy suitable for their MCP host.

> **MACHINE TRUTH REQUIRED:** If the live public API exposes retry hints, rate limits, or recommended polling intervals, document them here exactly.

## Artifact availability is subordinate to job outcome

Clients should reason about job state before presenting artifact availability.

Correct:

```text
job.status == failed
-> terminal failure
-> artifact unavailable is explained as part of failed outcome
```

Incorrect:

```text
artifact.available == false
-> "not finished yet"
```

The incorrect form can misrepresent a terminal failure as temporary incompleteness.
