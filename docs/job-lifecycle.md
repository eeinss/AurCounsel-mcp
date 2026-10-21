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

The full stage sequence of every capability is in [Stage lists](#stage-lists-all-capabilities) below.

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

## Fast Legal jobs

A `fast_legal` job follows the same states: `submitted` → `processing` → `completed` or `failed`. It has one artifact, `fast_answer` (Markdown). When the job is `completed`, `get_job` also returns the answer inline in `answer_markdown` and the evidence-sufficiency status in `evidence`:

```json
{
  "ok": true,
  "job_id": "0123456789abcdef",
  "capability": "fast_legal",
  "status": "completed",
  "progress": null,
  "answer_markdown": "...",
  "evidence": {
    "status": "COMPLETE",
    "insufficiency_reason": "",
    "review_outcome": "PASS"
  },
  "draft_check": {"class": "A", "changes": 0},
  "sources": [ ... ],
  "sources_summary": { ... },
  "artifacts": [{"name": "fast_answer", "ready": true}],
  "level": "medium",
  "cost": null,
  "cost_status": "unsupported"
}
```

> `evidence.status` is the answer review's own result (the interim marker used from 2026-10-17 is withdrawn as of 2026-10-20). An insufficient answer carries its reason in `insufficiency_reason`. The answer text itself carries no evidence-status line, and clients need not show `evidence` next to the answer. See [tools.md](tools.md#presenting-evidence-and-sources).

A failed `fast_legal` job is `status: "failed"` with no answer; `failure.error_code` is `RETRIEVAL_FAILED` or `FAST_UNAVAILABLE` (see [tools.md](tools.md#presenting-evidence-and-sources)).

`level` is the job's level (`medium` or `high`). A `high` job's `cost_status` is `not_final` while it is `processing` and `settled` once it is `completed` or `failed` (a failed job at 0); a `medium` job has `cost: null` and `cost_status: "unsupported"`. See [tools.md](tools.md#levels-and-cost-level-cost-cost_status).

`evidence.status` is `COMPLETE` or `INSUFFICIENT_EVIDENCE`. It is separate from the job `status`: a job that answered with `INSUFFICIENT_EVIDENCE` is still `completed`. See [tools.md](tools.md#fast_legal).

While a `fast_legal` job is `processing`, `progress` is its current step (`{"step", "text"}`). `get_job(job_id, after_seq)` also returns its progress events and the answer text as it is written. That text is a draft, and on `completed` the job's `answer_markdown` replaces it. Events are kept for one hour after the job ends. See [tools.md](tools.md#following-a-fast_legal-job-as-it-runs-after_seq).

A `completed` `fast_legal` job also carries `sources` and `sources_summary`: what the final answer cites, and what the job actually retrieved of each. Both are `null` while the job is not completed and on jobs submitted before sources were introduced. See [tools.md](tools.md#sources-sources-sources_summary).

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

`progress` carries `fraction` (a float), `stage` (a string), `stage_recognised` (a boolean, mirroring `status_recognised` for the stage vocabulary) and `text` (the current step in Chinese).

### Stage lists (all capabilities)

`progress.stage` is the job's current stage code; `progress.text` (since 2026-10-21) says the same step in Chinese, with its detail when there is one. Events (`get_job` with `after_seq`, any capability — see *Following a job's steps* below) carry a finer `step` code. Fractions are where the service sets `progress.fraction` on entering the stage.

**review — general review** (no `review_type`; `medium`):

| `stage` | event `step` | 中文 (`text`) | `fraction` | event `detail` |
|---|---|---|---|---|
| `parsing` | `parsing` | 解析合約 | 0.05 | |
| `parsed` | `parsed` | 合約解析完成 | 0.10 | |
| `identifying` | `classifying` | 識別合約類型與關鍵條款 | 0.15 | |
| `identified` | `classified` | 關鍵條款識別完成 | 0.25 | |
| `comparing` | `risk_review` | 逐條比對風險 | 0.26 → 0.53 | 共 N 條; 第 i／N 條:<clause heading> |
| `comparing` | `redlining` | 逐條產生修訂 | 0.55 → 0.85 | 共 N 條; 第 i／N 條:<clause heading> |
| `compared` | `analyzed` | 條款分析完成 | 0.85 | |
| `generating` | `memo` | 撰寫審閱意見書 | 0.90 | |
| `done` | `done` | 已完成 / 未完成 | 1.0 | |

A document over the length limit ends at `refused` (1.0).

**review — with `review_type`** (any level; `high` and `large` review only on this path):

| `stage` | event `step` | 中文 (`text`) | `fraction` |
|---|---|---|---|
| `parsing` | `parsing` | 解析合約 | 0 |
| `pass1` | `first_review` | 第一輪審閱:重要議題與修訂 | 0.20 |
| `pass2` | `additional_review` | 依類型議題補充審閱 | 0.60 |
| `delivering` | `redlining` | 產生修訂稿與紅線 | 0.90 |
| `done` | `done` | 已完成 / 未完成 | 1.0 |

**draft**:

| `stage` | event `step` | 中文 (`text`) | `fraction` | event `detail` |
|---|---|---|---|---|
| `retrieving` | `retrieving` | 檢索同類型範本與相關條款 | 0.10 | |
| `drafting` | `drafting` | 起草合約 | 0.30 | 共約 N 條, or the part being drafted, when the drafting step reports one |
| `drafting` | `assembling` | 彙整並組裝草稿 | 0.85 | |
| `done` | `done` | 已完成 / 未完成 | 1.0 | |

**revise** (not open yet):

| `stage` | event `step` | 中文 (`text`) | `fraction` | event `detail` |
|---|---|---|---|---|
| `locating` | `locating` | 定位要修改的條款 | 0.20 | |
| `revising` | `revising` | 修訂條款 | 0.30 → 0.70 | 第 i／N 條:<clause heading> |
| `assembling` | `assembling` | 組合修訂版本 | 0.75 | |
| `redlining` | `redlining` | 產生紅線 | 0.90 | |
| `done` | `done` | 已完成 / 未完成 | 1.0 | |

**compare** (not open yet):

| `stage` | event `step` | 中文 (`text`) | `fraction` | event `detail` |
|---|---|---|---|---|
| `parsing` | `parsing` | 解析兩份文件 | 0.05, 0.10 | 文件 A; 文件 B |
| `aligning` | `aligning` | 對齊兩份文件的段落 | 0.15 | 文件 A n 段・文件 B m 段 |
| `analyzing` | `analyzing` | 逐段分析差異 | 0.20 → 0.75 | 第 i／N 處變動 |
| `synthesizing` | `synthesizing` | 撰寫比對總評 | 0.78 | |
| `generating` | `generating` | 產生比對文件 | 0.85 | |
| `done` | `done` | 已完成 / 未完成 | 1.0 | |

`fraction` is a position, not a time estimate (a long step keeps one value for minutes), and it does not decrease. Treat `stage` as a display value, not something to branch on; branch on `status`.

### Following a job's steps (`after_seq`, all capabilities)

Pass `after_seq` to `get_job` (0 on the first poll, then the previous reply's `last_seq`): the reply adds `events` — only those after that number — and `last_seq`. Polling again with the same `after_seq` repeats nothing earlier, and `last_seq` never goes back. Each event is `{seq, ts, type, step, text, detail?}`: `type` `progress` is a step the job reached (from the job's own work, never a timer); the last event is `type: "done"` with `status` `completed` or `failed`. `detail` may name the clause by its number and heading from your own document, never its text. A job's events are kept for an hour after it ends. Example, a general review of a 10-clause contract (2026-10-21):

```text
1 parsing 解析合約 · 2 parsed 合約解析完成 · 3 classifying 識別合約類型與關鍵條款 · 4 classified 關鍵條款識別完成
5 risk_review 逐條比對風險 共 10 條 · 6 risk_review 第 1／10 條:價格政策 … 15 risk_review 第 10／10 條:合約期限與終止
16 redlining 逐條產生修訂 共 0 條 · 17 analyzed 條款分析完成 · 18 memo 撰寫審閱意見書 · 19 done 已完成
```

## Polling guidance

AurCounsel does not require a specific client polling interval. Clients should avoid tight loops and should use a reasonable retry/backoff strategy suitable for their MCP host.

For scale: the review jobs captured here took minutes, not seconds. The live `review_contract` description says the review "runs in the background and takes minutes." The one job polled end to end during this pass — a short, synthetic, eight-clause contract — was first read as `completed` 159 seconds after submission — that is when the tenth poll landed, not necessarily when the job finished. A longer document will take longer; that number is a single data point, not a service level.

Requests are rate-limited per client IP: at most 120 requests in a 60-second window; over the limit the server answers HTTP `429 Too Many Requests` with `Retry-After: 60`. Clients that share one egress IP share that budget, so keep polling intervals moderate (for example every 2–10 s for `fast_legal` — 2 s when following its events with `after_seq` — and every 20–30 s for longer jobs).

There is no cancel operation: once submitted, a job runs to its end. A client that no longer needs the result simply stops polling.

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
