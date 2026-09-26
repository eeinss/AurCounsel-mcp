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

This list is not inferred. The live `get_job` description states that `status` "is one of submitted, processing, completed, failed, or unknown."

The canonical field is the top-level `status`. Two adjacent fields qualify it:

| Field | Meaning |
|---|---|
| `status` | The mapped public status, from the five values above. |
| `status_recognised` | `false` when the engine reported a state this server does not map. |
| `upstream_status` | The engine's own raw string. Observed: `running` for `processing`, `done` for `completed`, `error` for `failed`. |

Which states were observed live:

| Status | Observed | How |
|---|---|---|
| `submitted` | in the submission response only | The `review_contract` response reported `status: "submitted"` for the job it had just created. No `get_job` read returned it — see the note under `submitted` below. |
| `processing` | yes | Nine consecutive `get_job` reads on one job submitted during this pass. |
| `completed` | yes | Two review jobs: one pre-existing, and the job submitted during this pass, polled through to its terminal state. |
| `failed` | yes | A pre-existing terminally failed review job. |
| `unknown` | **no** | Requires the engine to report an unmapped state. |

Everything below that is marked UNRESOLVED was not observed and is not guessed.

### `submitted`

AurCounsel has accepted the job into the public workflow, but processing is not yet reported as active or complete.

Client behavior:

- preserve the `job_id`;
- do not request or present a final deliverable as completed;
- check the job again according to the client's retry policy.

Observed once, and not where you would expect it: `submitted` was the `status` in the **`review_contract` submission response itself**, alongside the new `job_id`. The submission response is not a `get_job` response and does not carry `progress`, `summary`, or `artifacts`; see [tools.md](tools.md) for its exact shape.

**UNRESOLVED** — no `get_job` response with `status: "submitted"` was captured. The first poll went out 16 seconds after submission and already read `processing`. Whether `get_job` reports `submitted` at all, and for how long, is not established. Do not write a client that waits for a `submitted` reading before it starts polling.

### `processing`

AurCounsel is processing the job.

Client behavior:

- continue to treat the job as non-terminal;
- do not present intermediate or unavailable artifacts as final output;
- check the job again according to the client's retry policy.

Observed on one job, read nine times. The body carries the same top-level fields as a completed job, with three differences that a client has to handle:

- `upstream_status` was `running`, and `status_recognised` was `true`;
- every `summary` field was `null`;
- the `artifacts` array was **already fully populated** — all six review artifacts, with the same names, URLs, and media types they carry at completion — but every `ready` was `false`.

That last point is the one that bites. The presence of an entry in `artifacts` says nothing about whether the artifact exists. See [tools.md](tools.md) for the full body.

`progress` moved during the run. The readings, at a fixed 15-second sleep between polls (so each `t` also carries the preceding call's own latency), were:

| Poll | t (s) | `status` | `upstream_status` | `progress.fraction` | `progress.stage` |
|---|---|---|---|---|---|
| 1 | 16 | `processing` | `running` | 0.26 | `comparing` |
| 2 | 32 | `processing` | `running` | 0.29375 | `comparing` |
| 3 | 48 | `processing` | `running` | 0.9 | `generating` |
| 4–9 | 64, 80, 96, 111, 127, 143 | `processing` | `running` | 0.9 | `generating` |
| 10 | 159 | `completed` | `done` | 1.0 | `done` |

`fraction` did not decrease, and it is not a time estimate: it read `0.9` on seven consecutive polls, from `t=48` to `t=143`, and the job did not finish until `t=159`. `stage_recognised` was `true` at every reading. This is one job, of one capability, on one day — treat the numbers as an existence proof that `fraction` and `stage` move, not as a timing model.

**UNRESOLVED** — whether `fraction` can ever decrease, what its full stage sequence is, and how any of this behaves for `draft` or `compare` jobs.

### `completed`

The job completed successfully.

Client behavior:

- treat the job as terminal success;
- retrieve the required completed deliverable(s) with `get_artifact` according to the live artifact schema;
- handle an individually unavailable artifact as an artifact-level condition, not by rewriting the job status.

Observed shape — the synthetic contract submitted and polled through to completion during this pass (the identifier is a placeholder):

```json
{
  "ok": true,
  "job_id": "<JOB_ID>",
  "capability": "review",
  "status": "completed",
  "status_recognised": true,
  "upstream_status": "done",
  "progress": {"fraction": 1.0, "stage": "done", "stage_recognised": true},
  "summary": {
    "line": "審閱完成 — 8/8 條款已套用修訂",
    "clauses": 8, "replaced": 8, "have_revised": 8,
    "not_applied": 0, "states_status": "ok"
  },
  "artifacts": [
    {"name": "redline", "url": "https://mcp.clawplus.pro/artifact/<JOB_ID>/redline",
     "media_type": "text/html", "inline_text_available": true, "ready": true}
  ],
  "artifacts_blocked": null,
  "failure": null
}
```

The `artifacts` array is abridged above to one entry; the completed review job listed all six review artifacts, every one with `ready: true`. `summary` is capability-specific — the fields above are the review shape. [tools.md](tools.md) carries the same body unabridged.

`summary.line` is a human-readable sentence in the document's language and its wording varies with the outcome. Display it; do not parse it. The counts next to it are the machine-readable form.

Note that `completed` does not imply every requested change succeeded. The job above applied every clause it identified, but a second, pre-existing completed review job read during this work reported `not_applied: 1` while still returning `status: "completed"` and `states_status: "ok"` — the job finished; one requested change did not land. Read `summary`, not just `status`.

### `failed`

The job terminated without a successful completed result. **`failed` is a terminal state.** No amount of further polling changes it.

Client behavior:

- stop polling as if progress were still expected;
- surface the failure semantics returned by the public API;
- do not treat partial/generated internal artifacts as completed deliverables;
- do not convert `available: false` into a message implying that the artifact is merely "not ready yet" if the parent job is already terminal failed.

This distinction is intentional and is part of the public contract.

Observed shape:

```json
{
  "ok": true,
  "job_id": "<FAILED_JOB_ID>",
  "capability": "review",
  "status": "failed",
  "status_recognised": true,
  "upstream_status": "error",
  "progress": {"fraction": 0.15, "stage": "identifying", "stage_recognised": true},
  "summary": {"line": null, "clauses": null, "replaced": null,
              "have_revised": null, "not_applied": null, "states_status": null},
  "artifacts": [
    {"name": "redline", "url": "https://mcp.clawplus.pro/artifact/<FAILED_JOB_ID>/redline",
     "media_type": "text/html", "inline_text_available": true, "ready": false}
  ],
  "artifacts_blocked": null,
  "failure": {"error_code": "JOB_FAILED"}
}
```

Three things to read from that:

- the call itself succeeded — `ok` is `true` and the MCP result is not an error. The failure lives in the body. See [errors.md](errors.md).
- `artifacts` is still fully populated with six entries, all `ready: false`, each with a `url`. A populated `artifacts` array is **not** evidence that anything is retrievable.
- `progress` retains the fraction and stage the job reached before failing. `0.15` here is where it stopped, not how much is available.

**UNRESOLVED — failure detail.** The only `failure` content observed is `{"error_code": "JOB_FAILED"}`. Whether the block ever carries a message, a stage, or a more specific code was not established, and no enumeration of failure codes is exposed.

### `unknown`

`unknown` is a **result value**, not an error, and it does **not** mean the job could not be found.

It means the engine reported a state this server does not map to the public vocabulary. The live `get_job` description says so directly: "'unknown' means LegalOS reported a state this server does not map; the raw value is in `upstream_status`." `status_recognised` is `false` in that case.

Client behavior:

- do not interpret `unknown` as queued, pending, or processing;
- read and surface `upstream_status`;
- do not treat it as progress and do not treat it as terminal.

An identifier your identity did not submit — including one that resolves to no job — is refused with HTTP `403 Forbidden` before the tool runs. `JOB_NOT_FOUND` is the application error for a job your identity submitted that the service can no longer find; both are documented in [errors.md](errors.md).

**UNRESOLVED** — no live `unknown` response was observed. The description above is the server's own.

## Legal Research jobs

A `legal_research` job follows the same states: `submitted` → `processing` → `completed` or `failed`. It has one artifact, `research` (Markdown). When the job is `completed`, `get_job` also returns the result inline in `research_markdown`:

```json
{
  "ok": true,
  "job_id": "0123456789abcdef",
  "capability": "legal_research",
  "status": "completed",
  "research_markdown": "### ...",
  "artifacts": [{"name": "research", "ready": true}]
}
```

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

unknown = the engine reported a state this server does not map
          (read upstream_status); orthogonal to the flow above

JOB_NOT_FOUND = an application error, not a state
```

**Partially verified.** One job was followed from submission to a terminal state. The sequence actually read was: `submitted` in the submission response, then `processing` on nine consecutive `get_job` calls, then `completed`. That is one traversal of the left-hand path.

> **UNRESOLVED — transitions.** One traversal is not a state machine. The polls were 15 seconds apart, so any state the job passed through in less than that window would not appear in the readings — which is exactly the case for `submitted`, never seen from `get_job`. Whether direct transitions such as `submitted -> failed` occur, whether `draft` and `compare` jobs follow the same path, and whether a state can be observed twice non-consecutively were all not measured. The diagram shows the documented vocabulary plus one observed path, not a verified transition set. Do not build a client that requires a particular transition sequence; branch on the current `status`.

## Progress reporting

`progress` carries `fraction` (a float), `stage` (a string), and `stage_recognised` (a boolean, mirroring `status_recognised` for the stage vocabulary).

Observed stages, across all three review jobs read: `identifying` (on the failed job), `comparing`, `generating`, and `done`. `stage_recognised` was `true` at every reading.

**UNRESOLVED** — the stage vocabulary is not enumerated anywhere the public interface exposes. Four values were seen, on `review` jobs only; whether that is the complete review sequence, and what stages `draft` and `compare` report, is unknown. Treat `stage` as a display string, not as something to branch on.

## Polling guidance

AurCounsel does not require a specific client polling interval. Clients should avoid tight loops and should use a reasonable retry/backoff strategy suitable for their MCP host.

For scale: the review jobs captured here took minutes, not seconds. The live `review_contract` description says the review "runs in the background and takes minutes." The one job polled end to end during this pass — a short, synthetic, eight-clause contract — was first read as `completed` 159 seconds after submission — that is when the tenth poll landed, not necessarily when the job finished. A longer document will take longer; that number is a single data point, not a service level.

> **UNRESOLVED — retry hints and limits.** No rate-limit header, `retry_after` field, recommended interval, or throttling response was observed. Absence in a small read-only capture is not evidence that no limit exists.

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

The incorrect form can misrepresent a terminal failure as temporary incompleteness. This is not hypothetical: `get_artifact` on the terminally failed job returns a `note` that tells the caller to keep polling. Decide on `status`; do not relay that `note`. See [artifacts.md](artifacts.md).
