# Tools

This document describes the public purpose and behavioral contract of AurCounsel MCP tools. **Exact schemas must come from the live MCP server.** This file intentionally does not invent field names that have not been verified.

The schemas and descriptions reproduced verbatim below were captured from a live `tools/list` against `https://mcp.clawplus.pro/mcp`. Response bodies come from live calls on the same endpoint: one authorised `review_contract` submission of a synthetic contract, followed to `completed`, and one authorised `revise_contract` submission, likewise followed to `completed`. `revise_contract` is the one tool documented from its live run rather than from a discovery capture — its arguments and response fields are below, but no verbatim `inputSchema` block appears for it, because none was captured. Where a cell could not be captured, it is marked `UNRESOLVED` or `PENDING_AUTH` rather than filled in.

## Contract authority

For each tool, the authoritative order is:

1. live MCP tool discovery (`tools/list` or the equivalent exposed by the connected MCP client);
2. production request/response behavior;
3. this repository's documentation.

If this document differs from the machine-readable live contract, treat the difference as a documentation bug.

## Tool inventory (live capture)

`tools/list` returns exactly six tools:

```text
review_contract
draft_contract
compare_contracts
revise_contract
get_job
get_artifact
```

No additional public tools exist beyond these six. `prompts/list` returns `{"prompts": []}` and `resources/list` returns `{"resources": []}`.

Every tool's `inputSchema` is a JSON Schema `object` whose `title` has the form `<tool_name>Arguments`. Optional parameters are declared as `anyOf: [<type>, {"type": "null"}]` with `"default": null` — that is, an optional parameter may be omitted or passed explicitly as `null`.

> **Server identifier vs. product name.** The live `initialize` response reports `serverInfo.name` as `legalos`, and the tool descriptions below use that same string for the engine. `legalos` is the **server identifier returned on the wire by the live MCP deployment** — a compatibility identifier for clients that key off `serverInfo.name`, not a product name. The product documented by this repository is **AurCounsel**. Strings emitted by the server are reproduced exactly as received and are never rewritten; this repository's own prose says AurCounsel throughout.

---

## `review_contract`

### Purpose

Submit a contract to AurCounsel for contract review.

### Expected lifecycle

```text
review_contract
-> job_id
-> get_job(job_id)
-> completed | failed
-> get_artifact(...) when completed
```

### Public guarantees

- The operation is asynchronous.
- A successful submission identifies a job.
- Completed deliverables are retrieved through the artifact interface.
- A failed job must not expose partial/generated internal artifacts as completed deliverables.

### Live description (verbatim)

```text
Submit one contract for full LegalOS review.

    Returns immediately with a job_id; the review runs in the background and
    takes minutes. Poll get_job with that job_id.

    Args:
        file_name: Original file name, used as a label on the review.
        file_b64: The document, base64-encoded. .docx, .pdf and .doc are
            accepted and are identified by content, not by file name.
        requested_jurisdiction: Governing law to review under. 'hk' is accepted
            but LegalOS has no Hong Kong jurisdiction, so it is reviewed as
            'other' and the response says the request was degraded. Omit to let
            the engine detect the jurisdiction from the document.
        represented_party: Which side of the contract to review from, in your
            own words. LegalOS works on position, so this must resolve to one
            of party_a (甲方), party_b (乙方) or neutral — 'party A', '乙方',
            'both parties' and 'neutral' all resolve. A role such as
            'supplier' or 'licensor' does not: which position holds that role
            is a fact about this contract, and nothing here can read it, so the
            call is refused with PARTY_CONFIRMATION_REQUIRED and you are asked
            which position the client holds. Omit for the engine's own detection.
        contract_type_hint: Contract type in free text, e.g. 'nda', 'lease',
            '委任契約'. A hint only — an unrecognised value costs nothing.
```

### Exact input schema (verbatim)

```json
{
  "properties": {
    "file_name": { "title": "File Name", "type": "string" },
    "file_b64": { "title": "File B64", "type": "string" },
    "requested_jurisdiction": {
      "anyOf": [
        { "enum": ["taiwan", "mainland", "hk", "other"], "type": "string" },
        { "type": "null" }
      ],
      "default": null,
      "title": "Requested Jurisdiction"
    },
    "represented_party": {
      "anyOf": [{ "type": "string" }, { "type": "null" }],
      "default": null,
      "title": "Represented Party"
    },
    "contract_type_hint": {
      "anyOf": [{ "type": "string" }, { "type": "null" }],
      "default": null,
      "title": "Contract Type Hint"
    }
  },
  "required": ["file_name", "file_b64"],
  "title": "review_contractArguments",
  "type": "object"
}
```

| Field | Required | Type | Notes |
|---|---|---|---|
| `file_name` | yes | string | Label only. File type is identified by content, not by this name. |
| `file_b64` | yes | string | Base64 of the document. `.docx`, `.pdf`, `.doc` accepted. |
| `requested_jurisdiction` | no | enum \| null | `taiwan`, `mainland`, `hk`, `other`. `hk` is accepted but reviewed as `other`, and the response reports that the request was degraded. |
| `represented_party` | no | string \| null | Free text that must resolve to 甲方 / 乙方 / neutral. A role name (`supplier`, `licensor`) does not resolve and is refused with `PARTY_CONFIRMATION_REQUIRED`. |
| `contract_type_hint` | no | string \| null | Free-text hint; an unrecognised value is harmless. |

### Success response shape and `job_id` path

Captured from one `review_contract` submission executed against the live endpoint on 2026-08-31. The document submitted was a synthetic contract written for this capture; it contains no real party, and it is not part of this repository.

The MCP result carries exactly one content block, of type `text`. That block's `text` is itself a JSON document. `job_id` is a top-level key of that inner document:

```text
result.content[0].text  ->  parse as JSON  ->  job_id
```

The call returned in under a second. Response body, verbatim except that the job identifier is replaced with the placeholder `<JOB_ID>`:

```json
{
  "ok": true,
  "job_id": "<JOB_ID>",
  "capability": "review",
  "status": "submitted",
  "file_name": "synthetic_service_agreement.docx",
  "detected_kind": "docx",
  "jurisdiction": {
    "requested": "taiwan",
    "sent_to_engine": "taiwan",
    "degraded": false,
    "degradation_reason": null,
    "detected": null,
    "effective": "not_available",
    "note": "The engine may still override the requested jurisdiction from the document. That outcome is not exposed on the service interface."
  },
  "represented_party": "甲方",
  "represented_party_sent": "party_a",
  "contract_type_hint": null
}
```

Field notes, all from this one capture:

| Field | Note |
|---|---|
| `ok` | `true`. The MCP envelope also carried `isError: false`. |
| `job_id` | The handle. See the sensitivity note below. |
| `capability` | `review` for this tool. |
| `status` | `submitted` — the submission response reports the job's initial state directly. |
| `file_name` | Echo of the `file_name` argument. |
| `detected_kind` | `docx`. The type the server identified from content, not from the file name. |
| `jurisdiction` | Echo plus disposition; `degraded` was `false` because `taiwan` is a supported value. `effective` was `not_available` at submission time. |
| `represented_party` | Echo of the argument as sent (`甲方`). |
| `represented_party_sent` | The resolved position the engine was given: `party_a`. The free-text argument is normalized, and the response shows both sides of that resolution. |
| `contract_type_hint` | `null`; the argument was omitted. |

> **Treat `job_id` as sensitive.** The server `instructions` call it "the only handle to that job" and say to treat it as a credential. Anyone holding it can read that job's state and request its deliverables. Do not paste a real `job_id`, or any artifact reference or URL returned alongside it, into a public issue, log, or chat.

**What this capture does not establish.** `PARTY_CONFIRMATION_REQUIRED` was not triggered — the submission supplied a `represented_party` that resolves — so its response shape is still unobserved. One successful submission is also not a vocabulary: whether other fields appear on other inputs, or for `draft_contract` and `compare_contracts`, was not measured.

### Invalid-request error shape

Two distinct layers were observed on the read-only tools and apply here as well; see [errors.md](errors.md) for exact envelopes:

- a missing required argument is a **tool error** (`isError: true`) carrying a pydantic validation message;
- an argument that is present but unusable is an **application error returned as a successful call** (`isError: false`, body `{"ok": false, "error_code": "INVALID_INPUT", ...}`).

### Verified example

One submission was executed. The JSON-RPC envelope is the same as every other call on this page — `{"jsonrpc":"2.0","id":<n>,"method":"tools/call","params":{"name":"review_contract","arguments":{...}}}`. The `arguments` object sent was:

```json
{
  "file_name": "synthetic_service_agreement.docx",
  "file_b64": "<base64 of a .docx; 50072 characters in this call>",
  "requested_jurisdiction": "taiwan",
  "represented_party": "甲方"
}
```

`file_b64` is the only redacted value: it is the document itself, and its literal content is not a fact about the interface. Everything else is verbatim. The response is the body shown above; the resulting job was then polled to a terminal state with `get_job` — see [job-lifecycle.md](job-lifecycle.md) for the full observed sequence.

This page does not carry a copy-pasteable submission command. Sending one creates a real job. The `curl` page marks its submission block **NOT EXECUTED** for the same reason; see [../examples/curl.md](../examples/curl.md).

---

## `draft_contract`

### Purpose

Submit a contract drafting request to AurCounsel.

### Public guarantees

- The operation is asynchronous unless the live schema explicitly states otherwise.
- A successful submission identifies a job.
- Final drafting deliverables are retrieved only after successful completion.

### Live description (verbatim)

```text
Draft a new contract or legal document with LegalOS.

    Returns immediately with a job_id; the drafting runs in the background and
    takes minutes. Poll get_job with that job_id.

    Any field left blank is written into the document as a placeholder such as
    [甲方] and is not invented by the engine, so it is better to omit a term you
    do not know than to guess it.

    Args:
        subject: What the document is about — the subject matter or service
            being contracted for. Required on every draft.
        contract_type: The kind of contract, e.g. '委任契約', 'nda', '电商合同'.
            Required when drafting a contract, which is the default; omit it
            only together with a doc_type that is not a contract.
        party_a: Name of 甲方. Blank leaves a [甲方] placeholder.
        party_b: Name of 乙方. Blank leaves a [乙方] placeholder.
        amount: Contract amount, in your own wording. Blank leaves a placeholder.
        term: Contract term or duration. Blank leaves a placeholder.
        special: Any special requirements the document must cover.
        doc_type: For a court or lawyer's document rather than a contract:
            聲請書 / 起訴狀 / 答辯狀 / 存證信函 / 律師函 / 委任狀 / 和解書. Omit
            for a contract.
        requested_jurisdiction: Governing law to draft under. 'hk' is accepted
            but LegalOS has no Hong Kong jurisdiction, so it is drafted as
            'other' and the response says the request was degraded. Whether a
            jurisdiction is required is a property of the deployment, not of
            this call: where it is required, omitting it is refused upstream.
        represented_party: Which side the document is being drafted for, in
            your own words. LegalOS works on position, so this must resolve to
            one of party_a (甲方), party_b (乙方) or neutral. A role such as
            'supplier' or 'licensor' does not resolve: which position holds
            that role is a fact about this document, and nothing here can read
            it, so the call is refused with PARTY_CONFIRMATION_REQUIRED and you
            are asked which position the client holds. Omit to draft neutrally.
```

### Exact input schema (verbatim)

```json
{
  "properties": {
    "subject": { "title": "Subject", "type": "string" },
    "contract_type": { "anyOf": [{ "type": "string" }, { "type": "null" }], "default": null, "title": "Contract Type" },
    "party_a": { "anyOf": [{ "type": "string" }, { "type": "null" }], "default": null, "title": "Party A" },
    "party_b": { "anyOf": [{ "type": "string" }, { "type": "null" }], "default": null, "title": "Party B" },
    "amount": { "anyOf": [{ "type": "string" }, { "type": "null" }], "default": null, "title": "Amount" },
    "term": { "anyOf": [{ "type": "string" }, { "type": "null" }], "default": null, "title": "Term" },
    "special": { "anyOf": [{ "type": "string" }, { "type": "null" }], "default": null, "title": "Special" },
    "doc_type": { "anyOf": [{ "type": "string" }, { "type": "null" }], "default": null, "title": "Doc Type" },
    "requested_jurisdiction": {
      "anyOf": [
        { "enum": ["taiwan", "mainland", "hk", "other"], "type": "string" },
        { "type": "null" }
      ],
      "default": null,
      "title": "Requested Jurisdiction"
    },
    "represented_party": { "anyOf": [{ "type": "string" }, { "type": "null" }], "default": null, "title": "Represented Party" }
  },
  "required": ["subject"],
  "title": "draft_contractArguments",
  "type": "object"
}
```

`subject` is the only schema-required field. Note that the description declares `contract_type` to be required in practice when drafting a contract, and declares that whether `requested_jurisdiction` is required is a deployment property enforced upstream. Neither of those constraints is expressed in the JSON Schema.

### Success response shape and `job_id` path

**PENDING_AUTH.** Calling this tool creates a real job in the production system. The single submission executed during this verification pass went to `review_contract`; `draft_contract` was not called. The `job_id` path documented for `review_contract` is the MCP result shape and is very likely shared, but that is an inference, not a reading, and the rest of the body — which fields a `draft` submission echoes back — was not observed and is not guessed here.

### Verified example

**PENDING_AUTH** — no `draft_contract` request was executed.

---

## `compare_contracts`

### Purpose

Submit two contracts, versions, or other comparison inputs accepted by the live schema and ask AurCounsel to produce a comparison job.

### Public guarantees

- The comparison request produces a job identifier on successful submission.
- The job lifecycle is observed with `get_job`.
- Completed comparison deliverables are retrieved through `get_artifact`.

### Live description (verbatim)

```text
Compare two versions of a contract and report what changed.

    Returns immediately with a job_id; the comparison runs in the background and
    takes minutes. Poll get_job with that job_id.

    Both documents must be .docx. Unlike review, .pdf and .doc are not accepted
    here — the comparison pipeline reads Word documents only, and a file of
    another type is refused by content rather than by file name.

    Args:
        file_a_name: Original file name of the first contract, used as a label.
        file_a_b64: The first contract, base64-encoded .docx.
        file_b_name: Original file name of the second contract, used as a label.
        file_b_b64: The second contract, base64-encoded .docx.
```

### Exact input schema (verbatim)

```json
{
  "properties": {
    "file_a_name": { "title": "File A Name", "type": "string" },
    "file_a_b64": { "title": "File A B64", "type": "string" },
    "file_b_name": { "title": "File B Name", "type": "string" },
    "file_b_b64": { "title": "File B B64", "type": "string" }
  },
  "required": ["file_a_name", "file_a_b64", "file_b_name", "file_b_b64"],
  "title": "compare_contractsArguments",
  "type": "object"
}
```

All four fields are required. There are no optional fields and no enums. Both inputs must be `.docx` — unlike `review_contract`, `.pdf` and `.doc` are refused, by content rather than by file name.

### Success response shape and `job_id` path

**PENDING_AUTH.** Calling this tool creates a real job in the production system, and `compare_contracts` was not called. As with `draft_contract`, the response body for a `compare` submission was not observed and is not guessed here.

### Verified example

**PENDING_AUTH** — no `compare_contracts` request was executed.

---

## `revise_contract`

### Purpose

Submit a contract together with a revision instruction in prose, and get the revised contract back with a tracked-change redline.

### Expected lifecycle

```text
revise_contract
-> job_id
-> get_job(job_id)
-> completed | failed
-> read the revision outcome
-> get_artifact(...) when completed
```

### Public guarantees

- The operation is asynchronous, like the other submission tools.
- A successful submission identifies a job.
- A job that finishes is `completed` whether or not the revision was applied. `completed` reports that the job ran; the separate `revision` block on `get_job` reports what it did. See [`get_job`](#get_job).
- An instruction the server cannot tie to a clause of the submitted contract is not an error and not a guess: the job completes having declined to revise, and says why.
- Completed deliverables are retrieved through `get_artifact`: `revised_docx` and `redline_docx`.

### Arguments

| Field | Required | Type | Notes |
|---|---|---|---|
| `file_name` | yes | string | Label only, as for a review. |
| `file_b64` | one of the two | string | The document, base64-encoded. |
| `file_ref` | one of the two | string | A reference to the document, as the alternative to sending its bytes. |
| `revision_text` | yes | string | The revision instruction, in prose: which clause to change and what it should say. |

Send the document one way or the other — `file_b64` or `file_ref` — not both.

### How a clause is located

A clause number is the authoritative locator. If `revision_text` names an ordinal the document actually has — `第三條`, clause 3 — that clause is where the revision is applied, and nothing else in the instruction can move it: a description of the clause's subject or title may help find a clause, but it cannot override an ordinal the document has.

An ordinal the document does not have is the other case. Nothing is guessed and no other clause is substituted; the job completes having declined to revise, with the reason reported.

### Submission response

Same envelope as the other submission tools — one `text` content block whose text is a JSON object, with `job_id` at its top level:

| Field | Note |
|---|---|
| `ok` | `true` on a successful submission. |
| `job_id` | The handle. Treat it as sensitive; see the note under [`review_contract`](#success-response-shape-and-job_id-path). |
| `capability` | `revise` for this tool. |
| `status` | `submitted`. |
| `file_name` | Echo of the argument. |
| `detected_kind` | The type identified from content, not from the file name. |
| `revision_text` | Echo of the instruction. |

### Verified example

One `revise_contract` submission was executed: a synthetic contract plus one instruction naming the clause to change, followed to `completed`. The contract and the instruction are private fixtures and are not reproduced here, and — as on the `review_contract` section — this page carries no copy-pasteable submission command, because sending one creates a real job.

---

## `get_job`

### Purpose

Retrieve the current public state of a previously submitted AurCounsel job.

### Public status vocabulary

```text
submitted
processing
completed
failed
unknown
```

### Terminal semantics

- `completed` — terminal success. Completed deliverables may be retrieved according to the artifact contract.
- `failed` — terminal failure. Do not retry artifact retrieval on the assumption that the job is merely unfinished.
- `unknown` — the server received a state from the engine that it does not map. The raw engine value is carried in `upstream_status`. It is **not** the response for an unrecognised job identifier; that case is a `JOB_NOT_FOUND` application error (see [errors.md](errors.md)).

### Live description (verbatim)

```text
Get the state of any job submitted through this server.

    capability says which kind of job this is: review, draft or compare. It is
    null only for a job row the service could not classify, and the reply then
    also carries artifacts_blocked saying so.

    status is one of submitted, processing, completed, failed, or unknown.
    'unknown' means LegalOS reported a state this server does not map; the raw
    value is in upstream_status. A job that ran and failed comes back as
    'failed' with a failure block — LegalOS reports that in the body rather than
    as an HTTP error, so check the status and not just the call.

    artifacts lists what this job produces, each with a ready flag. If
    artifacts is empty there will be an artifacts_blocked block naming why no
    address could be built; an empty list on its own is never the answer.

    Args:
        job_id: The handle returned when the job was submitted.
```

Server-emitted strings are reproduced unchanged here. The live `capability` vocabulary also carries `revise`; the response field table below is the one to read for it.

### Exact input schema (verbatim)

```json
{
  "properties": { "job_id": { "title": "Job Id", "type": "string" } },
  "required": ["job_id"],
  "title": "get_jobArguments",
  "type": "object"
}
```

### Exact response shape

The tool returns `isError: false` and a single text content block containing this JSON object:

| Field | Type | Meaning |
|---|---|---|
| `ok` | boolean | `true` on a resolved job; `false` on an application error (see [errors.md](errors.md)). |
| `job_id` | string | Echo of the requested identifier. |
| `capability` | string \| null | `review`, `draft`, `compare`, or `revise`. `null` only for an unclassifiable job row, in which case `artifacts_blocked` explains. |
| `status` | string | Canonical status. One of the five values above. |
| `status_recognised` | boolean | `false` when the engine's status did not map — which is what produces `status: "unknown"`. |
| `upstream_status` | string | The raw engine value behind `status`. Observed: `"done"` for `completed`, `"error"` for `failed`. |
| `progress.fraction` | number | 0.0–1.0. |
| `progress.stage` | string | Engine stage name. Observed: `"done"`, `"identifying"`. |
| `progress.stage_recognised` | boolean | Whether the stage name mapped. |
| `summary.line` | string \| null | Human-readable one-line summary; `null` on a failed job. |
| `summary.clauses` | integer \| null | Review only. |
| `summary.replaced` | integer \| null | Review only. |
| `summary.have_revised` | integer \| null | Review only. |
| `summary.not_applied` | integer \| null | Review only. |
| `summary.states_status` | string \| null | Observed: `"ok"`. |
| `revision` | object \| null | Revision jobs. The block below — this, not `status`, is where a revision's result is reported. |
| `revision.outcome` | string | What the revision did. Observed: `"applied"`. The server's recognised set holds three values; the other two are `needs_clarification`, for an instruction that could not be tied to a clause, and `blocked`. |
| `revision.outcome_recognised` | boolean | `false` when the engine's outcome did not map, as `status_recognised` is for `status`. |
| `revision.replaced` | integer | How many clauses were replaced. Observed: `1`, for a one-clause instruction. |
| `revision.not_applied` | integer | How many requested changes were not applied. Observed: `0`. |
| `revision.reason` | string \| null | Why the revision was not applied; `null` when it was. |
| `artifacts` | array | See below. Never empty without `artifacts_blocked`. |
| `artifacts_blocked` | object \| null | Present when no artifact address could be built. Observed `null` in both captures. |
| `failure` | object \| null | Present when `status` is `failed`. Observed: `{"error_code": "JOB_FAILED"}`. |

Each `artifacts[]` entry:

| Field | Type | Notes |
|---|---|---|
| `name` | string | Artifact name; this is the value to pass to `get_artifact` as `artifact`. |
| `url` | string | `https://mcp.clawplus.pro/artifact/<job_id>/<name>` |
| `media_type` | string | Observed: `text/html`, `text/markdown`, and the OOXML wordprocessing type. |
| `inline_text_available` | boolean | `false` for binary artifacts. |
| `ready` | boolean | Whether this artifact has been written. |

### Canonical status field

`status`, at the top level of the response body. Not `upstream_status`, and not `progress.stage`.

### Status values: what was and was not observed

| Value | Observed live? | Basis |
|---|---|---|
| `completed` | yes | Two completed review jobs, one of them polled from submission through to completion. |
| `failed` | yes | A terminally failed review job. |
| `processing` | yes | Nine consecutive `get_job` reads on the job submitted during this pass. |
| `submitted` | **only in the submission response** | The `review_contract` response reported `status: "submitted"` for the new job. No `get_job` call returned `submitted`: the first poll, 16 seconds after submission, already read `processing`. Whether `get_job` ever reports `submitted` — and for how long — was not established. |
| `unknown` | **UNRESOLVED** | Declared by the live tool description. It requires the engine to emit an unmapped state, which cannot be induced from the public interface. |

`unknown` is a **normal `get_job` result value** — not a tool error, and not a request-validation outcome. That is stated by the live tool description; the behavior itself was not observed.

### Verified examples

**Completed job** — request:

```json
{"jsonrpc":"2.0","id":1,"method":"tools/call",
 "params":{"name":"get_job","arguments":{"job_id":"<JOB_ID>"}}}
```

Response body — the tenth and final read on the synthetic contract submitted during this pass. Job identifiers are replaced with the placeholder `<JOB_ID>`; every other value is verbatim:

```json
{
  "ok": true,
  "job_id": "<JOB_ID>",
  "capability": "review",
  "status": "completed",
  "status_recognised": true,
  "upstream_status": "done",
  "progress": {
    "fraction": 1.0,
    "stage": "done",
    "stage_recognised": true
  },
  "summary": {
    "line": "審閱完成 — 8/8 條款已套用修訂",
    "clauses": 8,
    "replaced": 8,
    "have_revised": 8,
    "not_applied": 0,
    "states_status": "ok"
  },
  "artifacts": [
    {
      "name": "redline",
      "url": "https://mcp.clawplus.pro/artifact/<JOB_ID>/redline",
      "media_type": "text/html",
      "inline_text_available": true,
      "ready": true
    },
    {
      "name": "original",
      "url": "https://mcp.clawplus.pro/artifact/<JOB_ID>/original",
      "media_type": "text/html",
      "inline_text_available": true,
      "ready": true
    },
    {
      "name": "revised",
      "url": "https://mcp.clawplus.pro/artifact/<JOB_ID>/revised",
      "media_type": "text/html",
      "inline_text_available": true,
      "ready": true
    },
    {
      "name": "revised_docx",
      "url": "https://mcp.clawplus.pro/artifact/<JOB_ID>/revised_docx",
      "media_type": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
      "inline_text_available": false,
      "ready": true
    },
    {
      "name": "memo",
      "url": "https://mcp.clawplus.pro/artifact/<JOB_ID>/memo",
      "media_type": "text/html",
      "inline_text_available": true,
      "ready": true
    },
    {
      "name": "review_comments",
      "url": "https://mcp.clawplus.pro/artifact/<JOB_ID>/review_comments",
      "media_type": "text/markdown",
      "inline_text_available": true,
      "ready": true
    }
  ],
  "artifacts_blocked": null,
  "failure": null
}
```

`summary` is capability-specific; the fields above are the review shape. `completed` does not imply that every requested change landed — a second, pre-existing completed review job read during this work reported `not_applied: 1` while still returning `status: "completed"` and `states_status: "ok"`. Read `summary`, not just `status`.

**Job in progress** — same request shape. This is the first of nine `processing` reads on the job submitted during this pass, taken 16 seconds after submission:

```json
{
  "ok": true,
  "job_id": "<JOB_ID>",
  "capability": "review",
  "status": "processing",
  "status_recognised": true,
  "upstream_status": "running",
  "progress": {
    "fraction": 0.26,
    "stage": "comparing",
    "stage_recognised": true
  },
  "summary": {
    "line": null,
    "clauses": null,
    "replaced": null,
    "have_revised": null,
    "not_applied": null,
    "states_status": null
  },
  "artifacts": [
    {
      "name": "redline",
      "url": "https://mcp.clawplus.pro/artifact/<JOB_ID>/redline",
      "media_type": "text/html",
      "inline_text_available": true,
      "ready": false
    },
    {
      "name": "original",
      "url": "https://mcp.clawplus.pro/artifact/<JOB_ID>/original",
      "media_type": "text/html",
      "inline_text_available": true,
      "ready": false
    },
    {
      "name": "revised",
      "url": "https://mcp.clawplus.pro/artifact/<JOB_ID>/revised",
      "media_type": "text/html",
      "inline_text_available": true,
      "ready": false
    },
    {
      "name": "revised_docx",
      "url": "https://mcp.clawplus.pro/artifact/<JOB_ID>/revised_docx",
      "media_type": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
      "inline_text_available": false,
      "ready": false
    },
    {
      "name": "memo",
      "url": "https://mcp.clawplus.pro/artifact/<JOB_ID>/memo",
      "media_type": "text/html",
      "inline_text_available": true,
      "ready": false
    },
    {
      "name": "review_comments",
      "url": "https://mcp.clawplus.pro/artifact/<JOB_ID>/review_comments",
      "media_type": "text/markdown",
      "inline_text_available": true,
      "ready": false
    }
  ],
  "artifacts_blocked": null,
  "failure": null
}
```

Three things to read off this body, all of which matter to a client:

- The full `artifacts` array is present while the job is still running, with the same six names, the same URLs, and the same media types as at completion. Only `ready` differs. **The presence of an artifact entry is not a signal that the artifact exists.** Branch on `ready`, and on terminal `status`.
- Every `summary` field is `null` until the job finishes.
- `upstream_status` was `running` while public `status` was `processing`, and `status_recognised` was `true` — the mapping was in place, not a fallback.

**Terminally failed job** — same request shape, different identifier:

```json
{
  "ok": true,
  "job_id": "<FAILED_JOB_ID>",
  "capability": "review",
  "status": "failed",
  "status_recognised": true,
  "upstream_status": "error",
  "progress": { "fraction": 0.15, "stage": "identifying", "stage_recognised": true },
  "summary": {
    "line": null, "clauses": null, "replaced": null,
    "have_revised": null, "not_applied": null, "states_status": null
  },
  "artifacts": [
    { "name": "redline",         "url": "https://mcp.clawplus.pro/artifact/<FAILED_JOB_ID>/redline",         "media_type": "text/html",     "inline_text_available": true,  "ready": false },
    { "name": "original",        "url": "https://mcp.clawplus.pro/artifact/<FAILED_JOB_ID>/original",        "media_type": "text/html",     "inline_text_available": true,  "ready": false },
    { "name": "revised",         "url": "https://mcp.clawplus.pro/artifact/<FAILED_JOB_ID>/revised",         "media_type": "text/html",     "inline_text_available": true,  "ready": false },
    { "name": "revised_docx",    "url": "https://mcp.clawplus.pro/artifact/<FAILED_JOB_ID>/revised_docx",    "media_type": "application/vnd.openxmlformats-officedocument.wordprocessingml.document", "inline_text_available": false, "ready": false },
    { "name": "memo",            "url": "https://mcp.clawplus.pro/artifact/<FAILED_JOB_ID>/memo",            "media_type": "text/html",     "inline_text_available": true,  "ready": false },
    { "name": "review_comments", "url": "https://mcp.clawplus.pro/artifact/<FAILED_JOB_ID>/review_comments", "media_type": "text/markdown", "inline_text_available": true,  "ready": false }
  ],
  "artifacts_blocked": null,
  "failure": { "error_code": "JOB_FAILED" }
}
```

Note the shape of terminal failure: `ok` is still `true` — the *call* succeeded — `progress.fraction` is frozen wherever it stopped, every `artifacts[].ready` is `false`, and `failure.error_code` is set. A client that checks only `ok` will misread this job as healthy.

### Failure representation

`failure` is an object with at least `error_code`. The only value observed is `JOB_FAILED`. Whether other codes or additional fields (message, stage, cause) appear in this block is **UNRESOLVED** — one failed job is not a vocabulary.

### Retry / poll hints

**UNRESOLVED.** The live responses carry no `retry_after`, no polling interval, and no rate-limit fields. The server `instructions` and the tool descriptions say to poll until the status is `completed` or `failed`, without naming an interval. No rate limiting was encountered during this capture; that is not evidence that none exists.

One job was polled at a fixed 15-second interval and reached `completed` after ten reads. That interval was chosen by the caller, not recommended by the server, and one job is not a service-level characteristic. See [job-lifecycle.md](job-lifecycle.md) for the sequence.

---

## `get_artifact`

### Purpose

Retrieve a completed deliverable generated by AurCounsel.

### Public guarantees

- Artifact retrieval is for deliverables exposed by the public artifact contract.
- Artifact availability must not be interpreted independently of terminal job state.
- A failed job's partial/generated internal output is not a completed deliverable.

### Live description (verbatim)

```text
Read one artifact of a finished job.

    Text artifacts are returned as text. A .docx artifact is returned as a URL
    only: it is a binary deliverable meant to be downloaded, not carried through
    a JSON payload.

    Which artifact names are valid depends on what kind of job this is — call
    get_job first and read artifacts[].name. Artifacts do not all appear at
    once, so also read artifacts[].ready. Asking early is not an error: the
    reply says available: false.

    Args:
        job_id: The handle returned when the job was submitted.
        artifact: A public artifact name for this job's capability.
            A review offers redline (tracked-change view of the changes),
            original, revised, revised_docx (the revised contract to deliver),
            memo (the opinion document) and review_comments (the review opinion
            the LegalOS UI shows the lawyer).
            A draft offers draft_html (the drafted contract), draft_docx (the
            same contract to deliver) and draft_summary.
            A compare offers compare_redline (what changed between the two
            versions), compare_memo and compare_synthesis.
```

### Exact input schema (verbatim)

```json
{
  "properties": {
    "job_id": { "title": "Job Id", "type": "string" },
    "artifact": { "title": "Artifact", "type": "string" }
  },
  "required": ["job_id", "artifact"],
  "title": "get_artifactArguments",
  "type": "object"
}
```

The parameter is named `artifact`, not `artifact_type`. Both fields are required. The schema declares `artifact` as a plain string with no enum; the accepted vocabulary is enforced at call time and returned in the error body.

### Artifact vocabulary, response shape, and failure behavior

See [artifacts.md](artifacts.md), which carries the artifact vocabulary by capability, the response field table, and the observed responses for the available, binary, unavailable, and unknown-job cases.

---

## Schema synchronization checklist

Before a release of this repository, compare all six documented tools against one fresh live discovery capture. Verify:

- exact tool names;
- exact descriptions;
- required vs optional fields;
- JSON types;
- enums;
- defaults, if publicly declared;
- response shapes;
- public error responses;
- any newly added or removed tools.
