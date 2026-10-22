# Tools

This document describes the public purpose and behavioral contract of AurCounsel MCP tools. **Exact schemas must come from the live MCP server.** This file intentionally does not invent field names that have not been verified.

The schemas and descriptions reproduced verbatim below were captured from a live `tools/list` against `https://mcp.clawplus.pro/mcp`. Response bodies come from live calls on the same endpoint, starting with one authorised `review_contract` submission of a synthetic contract, followed to `completed`. The descriptions and schemas were last re-captured from the live `tools/list` on 2026-10-18; the `fast_legal` description and schema and the `get_job` description reflect the service as deployed on 2026-10-20. Where a cell could not be captured, it is marked `UNRESOLVED` or `PENDING_AUTH` rather than filled in.

## Contract authority

For each tool, the authoritative order is:

1. live MCP tool discovery (`tools/list` or the equivalent exposed by the connected MCP client);
2. production request/response behavior;
3. this repository's documentation.

If this document differs from the machine-readable live contract, treat the difference as a documentation bug.

## Tool inventory (live capture)

`tools/list` returns exactly thirteen tools:

```text
review_contract
draft_contract
compare_contracts
revise_contract
get_capabilities
fast_legal
get_job
get_artifact
get_article
search_statutes
search_judgments
search_interpretations
read_judgment
```

No additional public tools exist beyond these thirteen. Two of them are registered but **not open**: `compare_contracts` and `revise_contract` answer every call with `PERMISSION_DENIED` (see their sections). [`get_capabilities`](#get_capabilities) says which capabilities are open right now. `prompts/list` returns `{"prompts": []}` and `resources/list` returns `{"resources": []}`.

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
- `model` is optional and is a level: omitted (or `medium`) is the default, unchanged — any contract type, `represented_party` as a position (甲方 / 乙方 / neutral). [`get_capabilities`](#get_capabilities) lists the levels open now under `capabilities.review.models` (`medium`, `high`, `large`), each with `review.<level>.enabled`.
- **`high` and `large` review only the types in `get_capabilities` `review.review_types`** (on 2026-10-22: 住宅租賃 for 承租人, 國外團體旅遊 for 旅客, 搬家服務 for 委託搬家服務之消費者, 經銷 for 經銷商, 買賣 for 買受人, 軟體開發委託 for 委託方, 合夥 for 非執行業務合夥人, 收購意向書 for 出售股東, 保證 for 保證人, 金錢借貸 for 貸與人, 最高限額抵押 for 抵押人, 會計師委任 for 委任人, 不動產附負擔贈與 for 贈與人). To use them send `review_type` (one of those types) and `client_instructions` (what the client wants from the review); `represented_party` may be omitted — the type fixes it, and a different one is refused (`INVALID_INPUT`, `context.field: "represented_party"`, `expected`). `high` or `large` without `review_type` is refused with `INVALID_INPUT`, `context: {"field": "model", "detail": "model_not_open_for_review_type", "open_review_types": [...]}`; an unknown `review_type` with `context.field: "review_type"` and `accepted`; a missing `client_instructions` with `context.field: "client_instructions"`. Each refusal comes before the document is used: nothing is sent and no job is created. A review is never switched to another level, nor to the general review.
- `review_type` also works at `medium`: the same type-specific review on the default level. Without `review_type` a review is the general review, as before.
- **Cost:** a `high` or `large` review is charged by usage, as a `high` / `large` draft (`get_job` `cost`, `cost_status`); a review that does not complete costs nothing. `medium` is not charged.
- **Deliverables of a `review_type` review:** `review_comments` (the review findings, including the additional findings), `revised_docx`, `redline`, `original`, `revised`, `memo`.
- Completed deliverables are retrieved through the artifact interface.
- A failed job must not expose partial/generated internal artifacts as completed deliverables.

### Live description (verbatim)

```text
Submit one contract for full LegalOS review.

    Returns immediately with a job_id; the review runs in the background and
    takes minutes. Poll get_job with that job_id.

    The document arrives one of two ways, and the call must use exactly one of
    them: `file_ref`, the handle returned by POSTing the document to `/upload`,
    or `file_b64`, the document base64-encoded in this argument. Supplying both
    is refused and so is supplying neither — neither one is a default and
    neither falls back to the other, so which document was reviewed is never a
    question about precedence.

    Args:
        file_name: Original file name, used as a label on the review. Required
            on both paths: it labels the review, and it is not what identifies
            the document — that is done by content.
        file_ref: A handle from `/upload`, held for a limited time, usable only
            by the caller that uploaded it. The document was identified and
            checked when it was uploaded; that result is what this review uses.
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
            which position the client holds. Required: there is no detection to
            fall back on, and a call without it is refused with INVALID_INPUT
            before anything is sent.
        contract_type_hint: Contract type in free text, e.g. 'nda', 'lease',
            '委任契約'. A hint only — an unrecognised value costs nothing.
        model: Optional. The review level: medium (the default), high or large.
            get_capabilities lists the levels open now
            (capabilities.review.models) and those built
            (implemented_models). A built level that is not open is refused
            with PERMISSION_DENIED before the document is read; any other value
            with INVALID_INPUT. high and large review only the types in
            get_capabilities review.review_types, so they need review_type;
            without it the call is refused with INVALID_INPUT (field model,
            open_review_types lists them). The review is never switched to
            another level.
        review_type: Optional. One of get_capabilities review.review_types
            (住宅租賃 / 國外團體旅遊 / 搬家服務 / 經銷 / 買賣 / 軟體開發委託 /
            合夥 / 收購意向書 / 保證 / 金錢借貸 /
            最高限額抵押 / 會計師委任 / 不動產附負擔贈與): the contract is reviewed for
            that type's one represented party (listed there), with the type's
            own review steps. represented_party may then be omitted; if given
            it must be that party. Needs client_instructions. contract_type_hint
            is not used on this path.
        client_instructions: The client's instructions for this review, in your
            own words (what the client wants from it). Required with
            review_type.
    
```

### Exact input schema (verbatim)

```json
{
  "properties": {
    "file_name": {
      "title": "File Name",
      "type": "string"
    },
    "file_b64": {
      "anyOf": [
        {
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "File B64"
    },
    "file_ref": {
      "anyOf": [
        {
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "File Ref"
    },
    "requested_jurisdiction": {
      "anyOf": [
        {
          "enum": [
            "taiwan",
            "mainland",
            "hk",
            "other"
          ],
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Requested Jurisdiction"
    },
    "represented_party": {
      "anyOf": [
        {
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Represented Party"
    },
    "contract_type_hint": {
      "anyOf": [
        {
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Contract Type Hint"
    },
    "model": {
      "anyOf": [
        {
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Model"
    },
    "review_type": {
      "anyOf": [
        {
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Review Type"
    },
    "client_instructions": {
      "anyOf": [
        {
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Client Instructions"
    }
  },
  "required": [
    "file_name",
    "represented_party"
  ],
  "title": "review_contractArguments",
  "type": "object"
}

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
            'other' and the response says the request was degraded. Required:
            omitting it is refused with MISSING_FIELD (context.field
            'jurisdiction') before anything is sent — ask the user.
            Pass it only when the user has stated the governing law. Do not
            infer it from the currency, a company's location, an address, the
            place of performance or a court name; if the user has not said it,
            ask the user.
        represented_party: Required for a contract (doc_type omitted): which side the document is being drafted for, in
            your own words; neutral drafts for both sides in balance. Omitting it for a contract is refused with INVALID_INPUT. LegalOS works on position, so this must resolve to
            one of party_a (甲方), party_b (乙方) or neutral. A role such as
            'supplier' or 'licensor' does not resolve: which position holds
            that role is a fact about this document, and nothing here can read
            it, so the call is refused with PARTY_CONFIRMATION_REQUIRED and you
            are asked which position the client holds.
            Pass it only when the user has said which side they represent; do
            not infer it from the same kind of clues, ask the user instead.
        model: Optional. The drafting level: medium (the default; free), high or large.
            省略 model 時為 medium(擬約預設);經銷、買賣及軟體開發委託契約另套用該契約類型的最低必要事項指引。
            high、large 只開放已驗證的契約類型(台灣、代表一方),各自開放的類型以 get_capabilities 的 draft.high / draft.large 的
            contract_types 為準;其他類型指定該等級會被拒絕(INVALID_INPUT,context.field model),不會改用其他等級。
            A level that is built but not open now (in get_capabilities implemented_models, not in models) is refused with
            PERMISSION_DENIED; any other value with INVALID_INPUT. A request is never switched to another level.

    Examples (one Taiwan request; the two calls differ only in model):

        1. Level omitted (medium):
            draft_contract(subject='會員系統的開發與上線', contract_type='軟體開發委託合約',
                           party_a='甲山零售股份有限公司', party_b='乙川數位有限公司',
                           amount='新臺幣一百二十萬元(未稅)', term='自簽約日起六個月',
                           special='分三期付款;系統上線後提供三個月保固。',
                           requested_jurisdiction='taiwan', represented_party='party_a')

        2. large, for a contract type open at that level (get_capabilities draft.large.contract_types):
            draft_contract(subject='住家室內裝修工程', contract_type='室內裝修工程承攬契約',
                           party_a='王小明', party_b='乙川室內裝修有限公司',
                           amount='新臺幣八十萬元(含稅)', term='自開工日起六十日',
                           special='分三期付款;完工驗收後保固一年。',
                           requested_jurisdiction='taiwan', represented_party='party_a',
                           model='large')
    
```

### Exact input schema (verbatim)

```json
{
  "properties": {
    "subject": {
      "title": "Subject",
      "type": "string"
    },
    "contract_type": {
      "anyOf": [
        {
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Contract Type"
    },
    "party_a": {
      "anyOf": [
        {
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Party A"
    },
    "party_b": {
      "anyOf": [
        {
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Party B"
    },
    "amount": {
      "anyOf": [
        {
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Amount"
    },
    "term": {
      "anyOf": [
        {
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Term"
    },
    "special": {
      "anyOf": [
        {
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Special"
    },
    "doc_type": {
      "anyOf": [
        {
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Doc Type"
    },
    "requested_jurisdiction": {
      "anyOf": [
        {
          "enum": [
            "taiwan",
            "mainland",
            "hk",
            "other"
          ],
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Requested Jurisdiction"
    },
    "represented_party": {
      "anyOf": [
        {
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Represented Party"
    },
    "model": {
      "anyOf": [
        {
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Model"
    }
  },
  "required": [
    "subject"
  ],
  "title": "draft_contractArguments",
  "type": "object"
}
```

`subject` is the only schema-required field. The server also requires, without the JSON Schema saying so: `contract_type` when drafting a contract, and **`requested_jurisdiction` for every draft** — a draft without it is refused with `MISSING_FIELD` and `context.field: "jurisdiction"` before anything is sent (no job is created). Ask the user for the governing law rather than inferring it.

**`represented_party` is required for a contract** (any draft without `doc_type`). The server refuses a contract draft without it with `INVALID_INPUT`. The live description says so, but its last sentence still reads "Omit to draft neutrally"; that sentence is out of date. To draft for both sides in balance, send `represented_party: "neutral"`.

`model` is optional and is a level: `medium` (the default), `high` or `large`. `get_capabilities` lists the levels open now under `capabilities.draft.models` (on 2026-10-20: `medium`, `high`, `large`) and the levels built under `implemented_models`. A built level that is not open is refused with `PERMISSION_DENIED`, `context: {"capability": "draft", "model": ...}`, with no job created; any other value with `INVALID_INPUT`.

- **Contract types with minimum-content guidance:** one list for every open level — [`get_capabilities`](#get_capabilities) `draft.<level>.contract_types` is the same for each (on 2026-10-20: 室內裝修工程承攬, interior fit-out works; 僱傭, employment under the Labor Standards Act; 金錢借貸, money loan; 冷藏食品配送運送, refrigerated food delivery carriage; 會計師委任, engagement of a CPA; 資訊系統維運與代管服務, IT operations and hosting services; 交通事故損害賠償和解, settlement of traffic-accident damages; 不動產附負擔贈與, gift of real property subject to a burden; 設備維護保養, equipment maintenance; 不動產委託銷售, an owner's brokerage listing of real property; 合資(共同設立股份有限公司), a joint venture forming a company limited by shares; 醫療軟體開發委託, custom software development in a medical setting; 銷售代理・居間(招攬客戶), a sales agency or brokerage soliciting customers for the principal; 經銷, distribution; 動產買賣(採購 / 供貨), sale, purchase and supply of goods; 軟體開發委託, commissioned software development; Taiwan law, a represented side). Whichever open level is chosen, a contract of such a type is drafted with that type's guidance.
- **Omitted / `medium`:** the drafting default. Other contract types take the general drafting path.
- **`high`, `large`:** **only** the listed contract types. With any other contract type, document type or jurisdiction the submission is refused and no job is created: `ok: false`, `error_code: "INVALID_INPUT"`, `context: {"field": "model", "submitted": ..., "detail": "model_not_open_for_contract_type"}`. It is **never switched to another level**; to draft that type, omit `model`.

### Success response shape and `job_id` path

**PENDING_AUTH.** Calling this tool creates a real job in the production system. The single submission executed during this verification pass went to `review_contract`; `draft_contract` was not called. The `job_id` path documented for `review_contract` is the MCP result shape and is very likely shared, but that is an inference, not a reading, and the rest of the body — which fields a `draft` submission echoes back — was not observed and is not guessed here.

### Verified example

**PENDING_AUTH** — no `draft_contract` request was executed.

---

## `compare_contracts`

### Purpose

**Not open.** Every call — with or without `model` — returns `ok: false`, `error_code: "PERMISSION_DENIED"`, `context.capability: "compare"`, before any document is read: nothing is sent, no job is created and no model is called. The capability is implemented on the service and is listed by [`get_capabilities`](#get_capabilities) with `enabled: false`, `implemented: true`; when it opens, that listing changes and this tool starts accepting calls.

### Public guarantees

- The comparison request produces a job identifier on successful submission.
- The job lifecycle is observed with `get_job`.
- Completed comparison deliverables are retrieved through `get_artifact`.

### Live description (verbatim)

```text
Compare two versions of a contract and report what changed.

    Not open yet: while the service's capability table has this capability
    disabled (see get_capabilities), every call is refused with
    PERMISSION_DENIED before any document is read — nothing is sent, no job is
    created and no model is called.

    Returns immediately with a job_id; the comparison runs in the background and
    takes minutes. Poll get_job with that job_id.

    Both documents must be .docx. Unlike review, .pdf and .doc are not accepted
    here — the comparison pipeline reads Word documents only, and a file of
    another type is refused by content rather than by file name.

    The two documents arrive the same way as each other: either both as handles
    from `/upload` (`file_a_ref` with `file_b_ref`) or both as base64
    (`file_a_b64` with `file_b_b64`). A call that mixes the two is refused, as
    is one that gives both transports for a side or neither. The names are
    always required; they are labels, and they are not what identifies a
    document.

    Args:
        file_a_name: Original file name of the first contract, used as a label.
        file_b_name: Original file name of the second contract, used as a label.
        file_a_b64: The first contract, base64-encoded .docx.
        file_b_b64: The second contract, base64-encoded .docx.
        file_a_ref: Handle from `/upload` for the first contract.
        file_b_ref: Handle from `/upload` for the second contract.
        model: Optional. The level: medium (the default), high or large; get_capabilities lists
            the levels offered. Never switched to another level.
    
```

### Exact input schema (verbatim)

```json
{
  "properties": {
    "file_a_name": {
      "title": "File A Name",
      "type": "string"
    },
    "file_b_name": {
      "title": "File B Name",
      "type": "string"
    },
    "file_a_b64": {
      "anyOf": [
        {
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "File A B64"
    },
    "file_b_b64": {
      "anyOf": [
        {
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "File B B64"
    },
    "file_a_ref": {
      "anyOf": [
        {
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "File A Ref"
    },
    "file_b_ref": {
      "anyOf": [
        {
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "File B Ref"
    },
    "model": {
      "anyOf": [
        {
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Model"
    }
  },
  "required": [
    "file_a_name",
    "file_b_name"
  ],
  "title": "compare_contractsArguments",
  "type": "object"
}
```

`file_a_name` and `file_b_name` are always required. The two documents arrive the same way: either both inline (`file_a_b64` with `file_b_b64`) or both by reference from [`/upload`](#uploading-a-document-upload) (`file_a_ref` with `file_b_ref`). A call that mixes the two, or gives both or neither for one side, is refused with `INVALID_INPUT`. There are no enums. Both inputs must be `.docx` — unlike `review_contract`, `.pdf` and `.doc` are refused, by content rather than by file name.

### Success response shape and `job_id` path

Not reachable while the tool is closed: every call returns `PERMISSION_DENIED`, observed live on 2026-10-18 (with and without `model`).

### Verified example

```json
{"ok": false, "error_code": "PERMISSION_DENIED", "message": "This capability is not open yet (此功能尚未開放). Nothing was sent, no job was created and no model was called; context.capability names it, and get_capabilities lists what is open.", "context": {"capability": "compare"}}
```

---

## `revise_contract`

### Purpose

**Not open.** Every call — with or without `model` — returns `ok: false`, `error_code: "PERMISSION_DENIED"`, `context.capability: "revise"`, before any document is read: nothing is sent, no job is created and no model is called. The capability is implemented on the service and is listed by [`get_capabilities`](#get_capabilities) with `enabled: false`, `implemented: true`; when it opens, that listing changes and this tool starts accepting calls.

Jobs submitted before the tool was withdrawn on an earlier date can still be read by the identity that submitted them: `capability: "revise"`, a `revision` block (`outcome`: `applied`, `blocked` or `needs_clarification`, with `reason` when not applied), and for an applied revision `revised_docx` and `redline_docx` through `get_artifact`.

### Live description (verbatim)

```text
Apply a requested change to one contract and produce the revised document.

    Not open yet: while the service's capability table has this capability
    disabled (see get_capabilities), every call is refused with
    PERMISSION_DENIED before any document is read — nothing is sent, no job is
    created and no model is called.

    Returns immediately with a job_id; the revision runs in the background and
    takes minutes. Poll get_job with that job_id, then read the result with
    get_artifact.

    The document arrives one of two ways, and the call must use exactly one of
    them: `file_ref`, the handle returned by POSTing the document to `/upload`,
    or `file_b64`, the document base64-encoded in this argument. Supplying both
    is refused and so is supplying neither — neither one is a default and
    neither falls back to the other, so which document was revised is never a
    question about precedence.

    Every call is a first revision of the document it carries: the document sent
    here is a new source, so the revision is made against those bytes and not
    against anything an earlier call revised. To revise a revision, send the
    revised document back in a new call.

    Two outcomes are not failures and are reported by get_job rather than as
    errors: the change may be *blocked*, meaning a revised document was produced
    but is not deliverable, and it may *need clarification*, meaning the request
    could not be located in this contract. In both cases the job completes and
    there is no revised document to download; the reason comes back with the job.

    Args:
        file_name: Original file name, used only as a label. Required on both
            paths; it is not what identifies the document — that is done by
            content.
        revision_text: What to change, in your own words, e.g.
            '第三條的期間改成 12 個月' or 'strike the exclusivity clause'. This
            is the instruction the engine works from, so a request naming the
            clause and the wanted outcome is located more often than a general
            one. Required on every call.
        file_ref: A handle from `/upload`, held for a limited time, usable only
            by the caller that uploaded it.
        file_b64: The document, base64-encoded. .docx only — a revision
            produces a new .docx version of a .docx, and the kind is identified
            by content, not by file name.
        model: Optional. The level: medium (the default), high or large; get_capabilities lists
            the levels offered. Never switched to another level.
    
```

### Exact input schema (verbatim)

```json
{
  "properties": {
    "file_name": {
      "title": "File Name",
      "type": "string"
    },
    "revision_text": {
      "title": "Revision Text",
      "type": "string"
    },
    "file_b64": {
      "anyOf": [
        {
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "File B64"
    },
    "file_ref": {
      "anyOf": [
        {
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "File Ref"
    },
    "model": {
      "anyOf": [
        {
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Model"
    }
  },
  "required": [
    "file_name",
    "revision_text"
  ],
  "title": "revise_contractArguments",
  "type": "object"
}
```

---

## `get_capabilities`

### Purpose

Read what this deployment offers right now. Read-only: it creates no job and calls no model. Everything it returns is read from the service's own capability table at call time — the same table that opens or closes a tool.

### Response (live, 2026-10-22)

```json
{
  "ok": true,
  "draft": {
    "jurisdictions": [
      "taiwan",
      "mainland",
      "other"
    ],
    "represented_party": [
      "party_a",
      "party_b",
      "neutral"
    ],
    "medium": {
      "enabled": true,
      "contract_types": [
        {
          "type": "fitout",
          "name": "室內裝修工程承攬",
          "scope": "室內裝修工程承攬契約(既有建物,代表定作人):LS-08 Floor 驗證範圍"
        },
        {
          "type": "employment",
          "name": "僱傭(勞動契約)",
          "scope": "勞動基準法適用之僱傭契約(不定期・全職,代表雇主):LS-01 Floor 驗證範圍"
        },
        {
          "type": "loan",
          "name": "金錢借貸",
          "scope": "金錢消費借貸契約(個人貸與公司・附息・定期,代表貸與人):LS-13 Floor 驗證範圍"
        },
        {
          "type": "carriage_cold",
          "name": "冷藏食品配送運送",
          "scope": "企業間冷藏食品之長期配送運送契約(公路汽車運輸,代表託運人):LS-06 Floor 驗證範圍"
        },
        {
          "type": "mandate",
          "name": "會計師委任",
          "scope": "企業委任會計師或會計師事務所提供查核簽證、稅務申報等專業服務之委任契約(代表委任人):LS-09 Floor 驗證範圍"
        },
        {
          "type": "service",
          "name": "資訊系統維運與代管服務",
          "scope": "企業間雲端代管、系統維運與技術支援等持續性服務契約(得併含客製開發,代表服務使用方):LS-15 Floor 驗證範圍"
        },
        {
          "type": "settlement",
          "name": "交通事故損害賠償和解",
          "scope": "交通事故侵權損害賠償之和解契約(代表受害人,和解金受領方):LS-11 Floor 驗證範圍"
        },
        {
          "type": "gift",
          "name": "不動產附負擔贈與",
          "scope": "以不動產(房屋及其基地應有部分)為標的之附負擔贈與契約(代表贈與人):LS-10 Floor 驗證範圍"
        },
        {
          "type": "equip_maint",
          "name": "設備維護保養",
          "scope": "設備使用方場所內實體設備之年度維護保養契約(定期保養、故障叫修、遠端診斷與零件供應;不含資訊系統維運,代表設備使用方):LS-20 Floor 驗證範圍"
        },
        {
          "type": "brokerage_re",
          "name": "不動產委託銷售",
          "scope": "屋主委託不動產經紀業(仲介)銷售其不動產之居間契約(不含代銷、預售屋、租賃委託與買方委託承購,代表委託人):LS-14 Floor 驗證範圍"
        },
        {
          "type": "joint_venture",
          "name": "合資(共同設立股份有限公司)",
          "scope": "各方共同設立股份有限公司之合資協議(股東協議,代表委託律師之合資一方):LS-21 Floor 驗證範圍"
        },
        {
          "type": "sw_dev_medical",
          "name": "醫療軟體開發委託",
          "scope": "醫療領域之客製化軟體開發(承攬)契約(軟體可能屬醫療器材,或處理病歷、醫療、健康等特種個人資料;代表委託方):LS-19 Floor 驗證範圍"
        },
        {
          "type": "agency",
          "name": "銷售代理・居間(招攬客戶)",
          "scope": "甲方委託乙方為其招攬客戶、由甲方與客戶直接締約之銷售代理(代辦商)或居間契約(乙方以佣金為報酬,不買斷、不轉售、不持有存貨;不含經銷,代表甲方):LS-23 Floor 驗證範圍"
        },
        {
          "type": "distribution",
          "name": "經銷",
          "scope": "以「經銷」命名的契約(經銷 / 獨家經銷 / 經銷代理):經銷模組驗證範圍"
        },
        {
          "type": "purchase",
          "name": "動產買賣(採購 / 供貨)",
          "scope": "動產買賣、採購與長期供貨契約:買賣模組驗證範圍"
        },
        {
          "type": "sw_dev",
          "name": "軟體開發委託",
          "scope": "軟體 / 系統委託開發契約:軟體開發委託模組驗證範圍"
        }
      ],
      "jurisdiction": "taiwan",
      "represented_party": [
        "party_a",
        "party_b"
      ]
    },
    "large": {
      "enabled": true,
      "contract_types": [
        {
          "type": "fitout",
          "name": "室內裝修工程承攬",
          "scope": "室內裝修工程承攬契約(既有建物,代表定作人):LS-08 Floor 驗證範圍"
        },
        {
          "type": "employment",
          "name": "僱傭(勞動契約)",
          "scope": "勞動基準法適用之僱傭契約(不定期・全職,代表雇主):LS-01 Floor 驗證範圍"
        },
        {
          "type": "loan",
          "name": "金錢借貸",
          "scope": "金錢消費借貸契約(個人貸與公司・附息・定期,代表貸與人):LS-13 Floor 驗證範圍"
        },
        {
          "type": "carriage_cold",
          "name": "冷藏食品配送運送",
          "scope": "企業間冷藏食品之長期配送運送契約(公路汽車運輸,代表託運人):LS-06 Floor 驗證範圍"
        },
        {
          "type": "mandate",
          "name": "會計師委任",
          "scope": "企業委任會計師或會計師事務所提供查核簽證、稅務申報等專業服務之委任契約(代表委任人):LS-09 Floor 驗證範圍"
        },
        {
          "type": "service",
          "name": "資訊系統維運與代管服務",
          "scope": "企業間雲端代管、系統維運與技術支援等持續性服務契約(得併含客製開發,代表服務使用方):LS-15 Floor 驗證範圍"
        },
        {
          "type": "settlement",
          "name": "交通事故損害賠償和解",
          "scope": "交通事故侵權損害賠償之和解契約(代表受害人,和解金受領方):LS-11 Floor 驗證範圍"
        },
        {
          "type": "gift",
          "name": "不動產附負擔贈與",
          "scope": "以不動產(房屋及其基地應有部分)為標的之附負擔贈與契約(代表贈與人):LS-10 Floor 驗證範圍"
        },
        {
          "type": "equip_maint",
          "name": "設備維護保養",
          "scope": "設備使用方場所內實體設備之年度維護保養契約(定期保養、故障叫修、遠端診斷與零件供應;不含資訊系統維運,代表設備使用方):LS-20 Floor 驗證範圍"
        },
        {
          "type": "brokerage_re",
          "name": "不動產委託銷售",
          "scope": "屋主委託不動產經紀業(仲介)銷售其不動產之居間契約(不含代銷、預售屋、租賃委託與買方委託承購,代表委託人):LS-14 Floor 驗證範圍"
        },
        {
          "type": "joint_venture",
          "name": "合資(共同設立股份有限公司)",
          "scope": "各方共同設立股份有限公司之合資協議(股東協議,代表委託律師之合資一方):LS-21 Floor 驗證範圍"
        },
        {
          "type": "sw_dev_medical",
          "name": "醫療軟體開發委託",
          "scope": "醫療領域之客製化軟體開發(承攬)契約(軟體可能屬醫療器材,或處理病歷、醫療、健康等特種個人資料;代表委託方):LS-19 Floor 驗證範圍"
        },
        {
          "type": "agency",
          "name": "銷售代理・居間(招攬客戶)",
          "scope": "甲方委託乙方為其招攬客戶、由甲方與客戶直接締約之銷售代理(代辦商)或居間契約(乙方以佣金為報酬,不買斷、不轉售、不持有存貨;不含經銷,代表甲方):LS-23 Floor 驗證範圍"
        },
        {
          "type": "distribution",
          "name": "經銷",
          "scope": "以「經銷」命名的契約(經銷 / 獨家經銷 / 經銷代理):經銷模組驗證範圍"
        },
        {
          "type": "purchase",
          "name": "動產買賣(採購 / 供貨)",
          "scope": "動產買賣、採購與長期供貨契約:買賣模組驗證範圍"
        },
        {
          "type": "sw_dev",
          "name": "軟體開發委託",
          "scope": "軟體 / 系統委託開發契約:軟體開發委託模組驗證範圍"
        }
      ],
      "jurisdiction": "taiwan",
      "represented_party": [
        "party_a",
        "party_b"
      ]
    },
    "high": {
      "enabled": true,
      "contract_types": [
        {
          "type": "fitout",
          "name": "室內裝修工程承攬",
          "scope": "室內裝修工程承攬契約(既有建物,代表定作人):LS-08 Floor 驗證範圍"
        },
        {
          "type": "employment",
          "name": "僱傭(勞動契約)",
          "scope": "勞動基準法適用之僱傭契約(不定期・全職,代表雇主):LS-01 Floor 驗證範圍"
        },
        {
          "type": "loan",
          "name": "金錢借貸",
          "scope": "金錢消費借貸契約(個人貸與公司・附息・定期,代表貸與人):LS-13 Floor 驗證範圍"
        },
        {
          "type": "carriage_cold",
          "name": "冷藏食品配送運送",
          "scope": "企業間冷藏食品之長期配送運送契約(公路汽車運輸,代表託運人):LS-06 Floor 驗證範圍"
        },
        {
          "type": "mandate",
          "name": "會計師委任",
          "scope": "企業委任會計師或會計師事務所提供查核簽證、稅務申報等專業服務之委任契約(代表委任人):LS-09 Floor 驗證範圍"
        },
        {
          "type": "service",
          "name": "資訊系統維運與代管服務",
          "scope": "企業間雲端代管、系統維運與技術支援等持續性服務契約(得併含客製開發,代表服務使用方):LS-15 Floor 驗證範圍"
        },
        {
          "type": "settlement",
          "name": "交通事故損害賠償和解",
          "scope": "交通事故侵權損害賠償之和解契約(代表受害人,和解金受領方):LS-11 Floor 驗證範圍"
        },
        {
          "type": "gift",
          "name": "不動產附負擔贈與",
          "scope": "以不動產(房屋及其基地應有部分)為標的之附負擔贈與契約(代表贈與人):LS-10 Floor 驗證範圍"
        },
        {
          "type": "equip_maint",
          "name": "設備維護保養",
          "scope": "設備使用方場所內實體設備之年度維護保養契約(定期保養、故障叫修、遠端診斷與零件供應;不含資訊系統維運,代表設備使用方):LS-20 Floor 驗證範圍"
        },
        {
          "type": "brokerage_re",
          "name": "不動產委託銷售",
          "scope": "屋主委託不動產經紀業(仲介)銷售其不動產之居間契約(不含代銷、預售屋、租賃委託與買方委託承購,代表委託人):LS-14 Floor 驗證範圍"
        },
        {
          "type": "joint_venture",
          "name": "合資(共同設立股份有限公司)",
          "scope": "各方共同設立股份有限公司之合資協議(股東協議,代表委託律師之合資一方):LS-21 Floor 驗證範圍"
        },
        {
          "type": "sw_dev_medical",
          "name": "醫療軟體開發委託",
          "scope": "醫療領域之客製化軟體開發(承攬)契約(軟體可能屬醫療器材,或處理病歷、醫療、健康等特種個人資料;代表委託方):LS-19 Floor 驗證範圍"
        },
        {
          "type": "agency",
          "name": "銷售代理・居間(招攬客戶)",
          "scope": "甲方委託乙方為其招攬客戶、由甲方與客戶直接締約之銷售代理(代辦商)或居間契約(乙方以佣金為報酬,不買斷、不轉售、不持有存貨;不含經銷,代表甲方):LS-23 Floor 驗證範圍"
        },
        {
          "type": "distribution",
          "name": "經銷",
          "scope": "以「經銷」命名的契約(經銷 / 獨家經銷 / 經銷代理):經銷模組驗證範圍"
        },
        {
          "type": "purchase",
          "name": "動產買賣(採購 / 供貨)",
          "scope": "動產買賣、採購與長期供貨契約:買賣模組驗證範圍"
        },
        {
          "type": "sw_dev",
          "name": "軟體開發委託",
          "scope": "軟體 / 系統委託開發契約:軟體開發委託模組驗證範圍"
        }
      ],
      "jurisdiction": "taiwan",
      "represented_party": [
        "party_a",
        "party_b"
      ]
    }
  },
  "review": {
    "represented_party": [
      "party_a",
      "party_b",
      "neutral"
    ],
    "review_types": [
      {
        "type": "住宅租賃",
        "represented_party": "承租人"
      },
      {
        "type": "國外團體旅遊",
        "represented_party": "旅客"
      },
      {
        "type": "搬家服務",
        "represented_party": "委託搬家服務之消費者"
      },
      {
        "type": "經銷",
        "represented_party": "經銷商"
      },
      {
        "type": "買賣",
        "represented_party": "買受人"
      },
      {
        "type": "軟體開發委託",
        "represented_party": "委託方"
      },
      {
        "type": "合夥",
        "represented_party": "非執行業務合夥人"
      },
      {
        "type": "收購意向書",
        "represented_party": "出售股東"
      },
      {
        "type": "保證",
        "represented_party": "保證人"
      },
      {
        "type": "金錢借貸",
        "represented_party": "貸與人"
      },
      {
        "type": "最高限額抵押",
        "represented_party": "抵押人"
      },
      {
        "type": "會計師委任",
        "represented_party": "委任人"
      },
      {
        "type": "不動產附負擔贈與",
        "represented_party": "贈與人"
      }
    ],
    "medium": {
      "enabled": true
    },
    "large": {
      "enabled": true,
      "review_types": [
        {
          "type": "住宅租賃",
          "represented_party": "承租人"
        },
        {
          "type": "國外團體旅遊",
          "represented_party": "旅客"
        },
        {
          "type": "搬家服務",
          "represented_party": "委託搬家服務之消費者"
        },
        {
          "type": "經銷",
          "represented_party": "經銷商"
        },
        {
          "type": "買賣",
          "represented_party": "買受人"
        },
        {
          "type": "軟體開發委託",
          "represented_party": "委託方"
        },
        {
          "type": "合夥",
          "represented_party": "非執行業務合夥人"
        },
        {
          "type": "收購意向書",
          "represented_party": "出售股東"
        },
        {
          "type": "保證",
          "represented_party": "保證人"
        },
        {
          "type": "金錢借貸",
          "represented_party": "貸與人"
        },
        {
          "type": "最高限額抵押",
          "represented_party": "抵押人"
        },
        {
          "type": "會計師委任",
          "represented_party": "委任人"
        },
        {
          "type": "不動產附負擔贈與",
          "represented_party": "贈與人"
        }
      ]
    },
    "high": {
      "enabled": true,
      "review_types": [
        {
          "type": "住宅租賃",
          "represented_party": "承租人"
        },
        {
          "type": "國外團體旅遊",
          "represented_party": "旅客"
        },
        {
          "type": "搬家服務",
          "represented_party": "委託搬家服務之消費者"
        },
        {
          "type": "經銷",
          "represented_party": "經銷商"
        },
        {
          "type": "買賣",
          "represented_party": "買受人"
        },
        {
          "type": "軟體開發委託",
          "represented_party": "委託方"
        },
        {
          "type": "合夥",
          "represented_party": "非執行業務合夥人"
        },
        {
          "type": "收購意向書",
          "represented_party": "出售股東"
        },
        {
          "type": "保證",
          "represented_party": "保證人"
        },
        {
          "type": "金錢借貸",
          "represented_party": "貸與人"
        },
        {
          "type": "最高限額抵押",
          "represented_party": "抵押人"
        },
        {
          "type": "會計師委任",
          "represented_party": "委任人"
        },
        {
          "type": "不動產附負擔贈與",
          "represented_party": "贈與人"
        }
      ]
    }
  },
  "revise": {
    "medium": {
      "enabled": false
    },
    "large": {
      "enabled": false
    }
  },
  "compare": {
    "medium": {
      "enabled": false
    },
    "large": {
      "enabled": false
    }
  },
  "models": {
    "medium": {},
    "high": {},
    "large": {}
  },
  "capabilities": {
    "draft": {
      "enabled": true,
      "implemented": true,
      "default_model": "medium",
      "models": [
        "medium",
        "high",
        "large"
      ],
      "implemented_models": [
        "medium",
        "high",
        "large"
      ]
    },
    "review": {
      "enabled": true,
      "implemented": true,
      "default_model": "medium",
      "models": [
        "medium",
        "high",
        "large"
      ],
      "implemented_models": [
        "medium",
        "high",
        "large"
      ]
    },
    "revise": {
      "enabled": false,
      "implemented": true,
      "default_model": "medium",
      "models": [],
      "implemented_models": [
        "medium",
        "large"
      ]
    },
    "compare": {
      "enabled": false,
      "implemented": true,
      "default_model": "medium",
      "models": [],
      "implemented_models": [
        "medium",
        "large"
      ]
    }
  }
}
```

### Live description (verbatim)

```text
What this deployment offers right now, read from the service's own table (nothing is cached here).

    Read-only; creates no job and calls no model. A `model` argument is a level: medium (the default; free, local), high or large.
    Returns:
      models: the levels offered.
      capabilities: per capability (draft, review, revise, compare) whether it is enabled for you now (`enabled`), whether it is built
        (`implemented` — a capability can be built and still not open, in which case its tool answers PERMISSION_DENIED), its default
        level (`default_model`, used when `model` is omitted), `models` — the levels open to you now — and `implemented_models` — the
        levels built; a level listed only in implemented_models is refused with PERMISSION_DENIED.
      draft / review / revise / compare: per implemented level, `{"enabled": true|false}`. For a level limited to some contract types
        (draft.high, draft.large) also `contract_types` (the types open now), `jurisdiction` and `represented_party`: draft_contract
        at that level accepts only those; any other request is refused (INVALID_INPUT, context.field model), never switched to another
        level.
      draft also: accepted jurisdictions and represented_party values. review also: accepted represented_party values.
    
```

### Exact input schema (verbatim)

```json
{
  "properties": {},
  "title": "get_capabilitiesArguments",
  "type": "object"
}
```

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

    capability says which kind of job this is: review, draft, compare or
    revise. It is null only for a job row the service could not classify, and
    the reply then also carries artifacts_blocked saying so.

    status is one of submitted, processing, completed, failed, or unknown.
    'unknown' means LegalOS reported a state this server does not map; the raw
    value is in upstream_status. A job that ran and failed comes back as
    'failed' with a failure block — LegalOS reports that in the body rather than
    as an HTTP error, so check the status and not just the call.

    revision is present only on a revise job, and it is where a revision's
    result lives: outcome is applied, blocked or needs_clarification, with
    reason for the two that are not applied. A revision that delivered nothing
    still completes — status alone does not say which of the three happened, so
    read this block before asking for the document.

    artifacts lists what this job produces, each with a ready flag. If
    artifacts is empty there will be an artifacts_blocked block naming why no
    address could be built; an empty list on its own is never the answer.

    progress (fast_legal) is the step the job is on now: step and a short
    Chinese text. To follow a fast_legal job as it runs, pass after_seq (0 on
    the first poll, then the last_seq of the previous reply): the reply adds
    events, only those after that number, and last_seq. Events are progress
    steps, text (the next piece of the answer while it is being written; join
    them in order) and a final done. The joined text is a draft: when status
    is completed, answer_markdown is the answer and replaces it, and
    draft_check.class says how they differ (A same, B citation / format
    clean-up only, C rewritten by the evidence review: tell the reader the
    shown text was replaced). A failed job's draft is not an answer. Polling
    again with the same after_seq is safe and repeats nothing earlier.

    review, draft, revise and compare follow the same way (bus 9462): pass
    after_seq and the reply adds events after it and last_seq. Each event is
    {seq, ts, type, step, text, detail?}: type progress is a step the job
    reached — step a fixed English code, text a short Chinese line, detail what
    it is on (a count, or the clause number and title it is on, e.g.
    第 12／40 條:第五條 違約金) — and the last is type done (status completed or
    failed). progress.text is the step the job is on now, in Chinese, with or
    without after_seq.

    sources (fast_legal, completed) lists the statutes and judgments the
    answer cites, each with retrieval saying what this run actually obtained
    of it (text / excerpt / listed for a statute; read / excerpt / listed for
    a judgment; cited_in_retrieved_judgment; not_retrieved, with no content).
    Content is only what was retrieved; a statute text that was cut short has
    text_truncated true. sources_summary counts them, and the retrieved results
    the answer does not cite. A source being listed does not mean the answer's
    legal analysis of it is correct. Jobs from before sources existed have
    null.

    cost / cost_status: cost is the amount the job is settled at,
    {amount_micros, currency, final}, present when cost_status is settled —
    fixed when the job ends; a failed job, including one interrupted by a
    service restart, is settled at 0. not_final: the job has not ended.
    unsupported: this capability / model has no settlement (currently
    draft_contract and fast_legal at levels high and large are settled;
    medium is not).

    Args:
        job_id: The handle returned when the job was submitted.
        after_seq: Return the job's events after this sequence number (0 on the first poll, then the previous last_seq).
    
```

Server-emitted strings are reproduced unchanged here. The live `capability` vocabulary also carries `revise`; the response field table below is the one to read for it. `after_seq` and the fields it adds are described in [Following a `fast_legal` job as it runs](#following-a-fast_legal-job-as-it-runs-after_seq).

### Exact input schema (verbatim)

```json
{
  "properties": {
    "job_id": {
      "title": "Job Id",
      "type": "string"
    },
    "after_seq": {
      "anyOf": [
        {
          "type": "integer"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "After Seq"
    }
  },
  "required": [
    "job_id"
  ],
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
| `summary.line` | string \| null | Human-readable one-line summary; `null` on a failed job and on a finished draft (read `draft_summary`). |
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

### Following a `fast_legal` job as it runs (`after_seq`)

`review`, `draft`, `revise` and `compare` jobs take `after_seq` too (since 2026-10-21): their events are work steps (`progress`) and a final `done` — no answer text. Each capability's steps are listed in [job-lifecycle.md](job-lifecycle.md#stage-lists-all-capabilities).

`get_job` takes an optional integer `after_seq`. Without it the reply is the one described above, so a client that only reads the finished result needs no change. With it — on a `fast_legal` job; other capabilities ignore it — the reply also carries:

| Field | Type | Meaning |
|---|---|---|
| `events` | array | The job's events whose `seq` is greater than `after_seq`, in order. |
| `last_seq` | integer | The highest `seq` known for the job. Send it as `after_seq` on the next poll. It is never lower than the `after_seq` you sent. |

A negative `after_seq` is refused with `INVALID_INPUT`, `context.field: "after_seq"`.

Every event has `seq` (an integer starting at 1 and strictly increasing within the job), `ts` (Unix time, seconds) and `type`:

| `type` | Further fields | Meaning |
|---|---|---|
| `progress` | `step`, `text` | The job moved on. `step` is `accepted`, `retrieval`, `answer`, `review` or `revise`; `text` is a short Chinese description, such as 「正在檢索法律資料…」 or a search label with its result count. |
| `text` | `text` | The next piece of the answer while it is being written. Join the `text` events in `seq` order. They are sent in batches of about half a second. |
| `done` | `status`, `text`, and `draft_check` (completed) or `run_event` (failed) | The job ended. It is always the last event. |

Events carry no model reasoning and no raw tool output: a search is reported as a label and a count.

While the job is `processing`, the top-level `progress` is the latest `progress` event as `{"step": ..., "text": ...}`, with or without `after_seq`. It is `null` once the job is terminal.

A `processing` reply with events:

```json
{
  "ok": true,
  "job_id": "0123456789abcdef",
  "capability": "fast_legal",
  "status": "processing",
  "progress": {"step": "answer", "text": "正在撰寫回答…"},
  "answer_markdown": null,
  "evidence": null,
  "draft_check": null,
  "artifacts": [{"name": "fast_answer", "ready": false}],
  "events": [
    {"seq": 21, "ts": 1792258110.52, "type": "progress", "step": "answer", "text": "正在撰寫回答…"},
    {"seq": 22, "ts": 1792258111.07, "type": "text", "text": "..."}
  ],
  "last_seq": 22
}
```

#### Draft and final answer

The text joined from `text` events is a **draft**, written before the evidence review has finished. When `status` is `completed`, `answer_markdown` is the answer: show it in place of the draft. Nothing is sent after `done`, so a later poll cannot overwrite the answer with draft text.

`draft_check` (on a completed job, with or without `after_seq`; `null` otherwise) says how the answer differs from the draft:

| `draft_check.class` | Meaning | What to show |
|---|---|---|
| `A` | Identical. | The answer. |
| `B` | Only citation or format clean-up, for example an unverified judgment number omitted or a quotation marked as a paraphrase. `changes` counts them. | The answer. |
| `C` | Rewritten by the evidence review. | The answer, and tell the reader that the text shown earlier was replaced. |

When `status` is `failed`, the draft is **not** an answer and must not be presented as a completed legal answer. `answer_markdown` and `evidence` are `null`.

#### Polling and reconnecting

```python
seq, draft = 0, ""
while True:
    job = get_job(job_id, after_seq=seq)        # one tools/call
    for event in job["events"]:
        if event["type"] == "progress":
            show_progress(event["text"])
        elif event["type"] == "text":
            draft += event["text"]
            show_draft(draft)
    seq = job["last_seq"]
    if job["status"] == "completed":
        show_answer(job["answer_markdown"], job["sources"], job["draft_check"])
        break
    if job["status"] == "failed":
        show_failure()                            # the draft is not an answer
        break
    time.sleep(2)
```

- Events belong to the `job_id` you poll, and `seq` counts within that job only. Keep one event list per job. When a new question starts a new job, start a new list at `after_seq` 0, and do not show an earlier job's progress or text under the new question.
- Polling again with the same `after_seq` is safe: it returns the same events and nothing earlier. If you merge replies, de-duplicate by `seq`.
- After a dropped connection or a restart of your client, continue with the last `last_seq` you processed. Events are kept by the service, so nothing is lost or repeated.
- Polling every 2 seconds worked in testing. The rate limit (120 requests per 60 seconds per client IP) is shared by every client behind one IP.
- Stop polling when `status` is `completed` or `failed`.

For scale, one production job on 2026-10-17, polled every 2 seconds, received its first `text` event about 21 seconds after submission and was `completed` at about 74 seconds, after 37 polls and about 46 KB of responses in total. That is a single data point, not a service level.

#### Retention

Events are kept for **1 hour after the job ends**. They are removed by a sweep that runs about every 15 minutes, so they can remain for up to about 75 minutes. After that, a poll with `after_seq` returns `events: []` and `last_seq` equal to the `after_seq` you sent. `status`, `answer_markdown`, `evidence` and `draft_check` are unchanged, and the answer itself is not removed.

There is no cancel operation, and no list of sources is returned.

### Cost (`cost`, `cost_status`)

Every `get_job` reply carries `cost_status`, and `cost` when it is settled:

| `cost_status` | `cost` | Meaning |
|---|---|---|
| `settled` | `{"amount_micros": <int>, "currency": "USD", "final": true}` | The amount this job is settled at. Fixed when the job ends: the first `completed` / `failed` reply already carries it, and every later read returns the same value. |
| `not_final` | `null` | The job has not ended yet. |
| `unsupported` | `null` | This capability or model has no settlement. Keep your own accounting for it. |

`amount_micros` is US dollars × 1,000,000 (an integer).

**What the amount is.** The amount the job is settled at, fixed when the job ends.

**Failed jobs are not charged:** a job that ends `failed` — including a draft cut short, stopped early or refused because the model was unavailable, and a job interrupted by a service restart — is settled at `amount_micros: 0`.

**Support matrix** (as deployed on 2026-10-20):

| Capability | Level | `cost_status` when finished |
|---|---|---|
| `draft_contract` | `high`, `large` | `settled` |
| `draft_contract` | omitted / `medium` | `unsupported` |
| `review_contract` | omitted / `medium` | `unsupported` |
| `compare_contracts`, `revise_contract` | — | not open (`PERMISSION_DENIED`) |
| `fast_legal` | `level: "high"` / `"large"` | `settled` (see [Levels and cost](#levels-and-cost-level-cost-cost_status)) |
| `fast_legal` | `level` omitted / `"medium"` | `unsupported` |


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
            A revision offers revised_docx (the revised contract to deliver)
            and redline_docx (the same revision as tracked changes). Both exist
            only for an applied revision — read revision.outcome from get_job.
    
```

### Exact input schema (verbatim)

```json
{
  "properties": {
    "job_id": {
      "title": "Job Id",
      "type": "string"
    },
    "artifact": {
      "title": "Artifact",
      "type": "string"
    }
  },
  "required": [
    "job_id",
    "artifact"
  ],
  "title": "get_artifactArguments",
  "type": "object"
}
```

The parameter is named `artifact`, not `artifact_type`. Both fields are required. The schema declares `artifact` as a plain string with no enum; the accepted vocabulary is enforced at call time and returned in the error body.

### Artifact vocabulary, response shape, and failure behavior

See [artifacts.md](artifacts.md), which carries the artifact vocabulary by capability, the response field table, and the observed responses for the available, binary, unavailable, and unknown-job cases.

---

## Uploading a document (`/upload`)

`file_ref` / `file_a_ref` / `file_b_ref` are handles to a document uploaded beforehand. Uploading is a plain HTTP request to the same host, not an MCP tool call, and carries the same `Authorization: Bearer <AURCOUNSEL_MCP_TOKEN>` header.

```bash
curl https://mcp.clawplus.pro/upload \
  -H "Authorization: Bearer $AURCOUNSEL_MCP_TOKEN" \
  --data-binary @contract.docx
```

- The body is the document's raw bytes — not multipart, not JSON, not base64. The `Content-Type` is not read; the file type is identified from content. No file name, query string or path segment is accepted; the name stays a tool argument (`file_name`).
- Success is HTTP 200 with a JSON body:

  ```json
  {"ok": true, "file_ref": "<FILE_REF>", "size": 123456, "sha256": "<SHA256>",
   "detected_kind": "docx", "integrity_status": "<STATUS>", "expires_at": "2026-01-01T00:00:00Z"}
  ```

- A `file_ref` is valid for **one hour** (`expires_at`), can be used only by the identity that uploaded it, and can be revoked early with `DELETE /upload` carrying the handle in the `x-legalos-file-ref` header (never in the URL). A ref that has expired, been revoked, or belongs to another identity is refused with `FILE_REF_NOT_USABLE`; upload the document again.
- The same document checks apply as for base64: at most **50 MB**; `.docx`, `.pdf` or `.doc` (compare accepts `.docx` only). Refusals carry the application error body with an HTTP status: `400` (`INVALID_INPUT`, `EMPTY_FILE`, `INVALID_FILE_PAYLOAD`), `413` (`FILE_TOO_LARGE`), `415` (`UNSUPPORTED_FILE_TYPE`); any method other than `POST` / `DELETE` is `405`.

## Schema synchronization checklist

Before a release of this repository, compare all documented tools against one fresh live discovery capture. Verify:

- exact tool names;
- exact descriptions;
- required vs optional fields;
- JSON types;
- enums;
- defaults, if publicly declared;
- response shapes;
- public error responses;
- any newly added or removed tools.

## `fast_legal`

### Purpose

Answer a legal question with bounded research and report whether the evidence found was sufficient. Fast Legal performs bounded legal research using AurCounsel's legal retrieval capabilities. `level`: `medium` (the default) is free and the fastest; `high` is charged by usage; `large` is charged by usage and researches the most deeply.

### Live description (verbatim)

```text
Answer a legal question with bounded research, and say whether the evidence found was sufficient.

    Fast Legal performs bounded legal research using AurCounsel's legal retrieval capabilities (statutes and court
    judgments) and returns an answer together with an evidence-sufficiency status:
    COMPLETE — the evidence found supports the core answer (it does not mean research was exhaustive);
    INSUFFICIENT_EVIDENCE — only part of the answer could be supported; evidence.insufficiency_reason says what and why.
    The status is model-assessed, not a guarantee. A run usually takes one to a few minutes.

    Returns immediately with a job_id. Poll get_job with that job_id; when status is completed the answer is in
    answer_markdown and the status in evidence (also available as get_artifact(job_id, "fast_answer")). When it is
    failed, failure.error_code says why: RETRIEVAL_FAILED — no statute or judgment could be retrieved (tried twice), so
    no answer was written; FAST_UNAVAILABLE — the run did not complete.

    Levels: medium (the default) is free and the fastest; high is charged by usage; large is charged by usage and
    researches the most deeply. For high and large, once the job is completed or failed, get_job returns cost
    {amount_micros, currency, final} with cost_status settled (a failed job is settled at 0). answer_markdown is the
    answer alone; read the charge from cost.

    Args:
        question: The legal question, in the user's own words.
        level: medium (default), high or large.
    
```

### Exact input schema (verbatim)

```json
{
  "properties": {
    "question": {
      "title": "Question",
      "type": "string"
    },
    "level": {
      "default": "medium",
      "enum": [
        "medium",
        "high",
        "large"
      ],
      "title": "Level",
      "type": "string"
    }
  },
  "required": [
    "question"
  ],
  "title": "fast_legalArguments",
  "type": "object"
}
```

### Parameters

| Parameter | Type | Required | Meaning |
| --- | --- | --- | --- |
| `question` | string | yes | The legal question, in the user's own words. Empty → `INVALID_INPUT` with `context: {"field": "question"}`. |
| `level` | string | no | `medium` (default): free, the fastest. `high`: charged by usage. `large`: charged by usage, the deepest research. Any other value → `INVALID_INPUT` with `context: {"field": "level"}`. |

### Lifecycle and result

The call returns immediately with `{"ok": true, "job_id": "...", "capability": "fast_legal", "status": "submitted"}`. Poll `get_job`: `status` moves from `processing` to `completed` (or `failed`); to follow the job while it runs, see [`after_seq`](#following-a-fast_legal-job-as-it-runs-after_seq). When `completed`, `answer_markdown` carries the answer as Markdown, `draft_check` says how it differs from the draft shown while it was written, `sources` lists what it cites (see [Sources](#sources-sources-sources_summary)), `evidence` carries the evidence-sufficiency status, and `artifacts` lists one artifact, `fast_answer`, which `get_artifact` returns as `text/markdown` together with the same `evidence`. Every reply also carries `level`, `cost` and `cost_status` (see [Levels and cost](#levels-and-cost-level-cost-cost_status)).

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

| `evidence` field | Meaning |
| --- | --- |
| `status` | `COMPLETE` — the evidence found supports the core answer (it does not mean the research was exhaustive). `INSUFFICIENT_EVIDENCE` — only part of the answer could be supported; the answer states what could and could not be confirmed, and why. |
| `insufficiency_reason` | Set only for `INSUFFICIENT_EVIDENCE`: what is missing and why. |
| `review_outcome` | Observability only: which internal review result produced the status (`PASS`, `REWRITE`, `INSUFFICIENT_EVIDENCE`, `NOT_RUN`, `UNREADABLE`). |

The status is **model-assessed**, not a guarantee. `INSUFFICIENT_EVIDENCE` does not mean the proposition is false or that no authority exists; it means bounded research did not gather enough to answer reliably.

**Evidence status (as of 2026-10-20).** `evidence.status` is the answer review's own result; the interim marker used from 2026-10-17 (every answer `INSUFFICIENT_EVIDENCE` with a fixed "unverified" reason) is withdrawn. The answer text carries no evidence-status line.

The status is not a legal verification of the answer. How to present `evidence` is up to the client: see [Presenting evidence and sources](#presenting-evidence-and-sources).

### Levels and cost (`level`, `cost`, `cost_status`)

`get_job` for a `fast_legal` job returns the job's `level` (`"medium"`, `"high"` or `"large"`) together with `cost` and `cost_status` (the general rules are in [Cost](#cost-cost-cost_status)):

| `level` | While `processing` | Once `completed` or `failed` |
|---|---|---|
| `medium` | `cost: null`, `cost_status: "unsupported"` | `cost: null`, `cost_status: "unsupported"` |
| `high`, `large` | `cost: null`, `cost_status: "not_final"` | `cost: {"amount_micros": <int>, "currency": "USD", "final": true}`, `cost_status: "settled"`. A failed job is settled at `amount_micros: 0`. |

`answer_markdown` (and the `fast_answer` artifact) is the answer alone. It does not include a cost line; read the charge from `cost`.

### Presenting evidence and sources

AurCounsel Fast Legal is meant to give practical, accurate legal analysis and advice. The answer in `answer_markdown` is the main content; `evidence` is supporting status information, not a score of whether the legal conclusion is correct.

- **You do not have to show `evidence.status` or its reason next to the answer.** You may leave it out of the main answer area or place it in a secondary details area.
- **Do keep real limitations accurate.** When a reply reports a genuine insufficiency (`INSUFFICIENT_EVIDENCE` with its own `insufficiency_reason`), a failed job, or another concrete limitation, do not present the answer as verified.
- **Use `sources` for legal sources.** You can offer expandable statute text, judgment excerpts and links, and distinguish what this job retrieved from citations it did not confirm (`not_retrieved`), as recorded per entry.
- `sources: null` means no source data is delivered for the job; it does not mean the job did no retrieval.
- Neither the presence of sources nor any evidence status guarantees that the legal conclusion is correct.

A failed `fast_legal` job is `status: "failed"` with no answer; `failure.error_code` is `RETRIEVAL_FAILED` (no statute or judgment could be retrieved, so no answer was written) or `FAST_UNAVAILABLE` (the run did not complete).

An insufficient answer has the same shape, with `status: "INSUFFICIENT_EVIDENCE"` and its own `insufficiency_reason`.

### Sources (`sources`, `sources_summary`)

When a `fast_legal` job is `completed`, `get_job` also returns `sources`: the statutes and judgments that `answer_markdown` cites, each with what this job actually retrieved of it. `sources_summary` counts them. Both are `null` while the job is not completed, when it failed, and on jobs submitted before sources were introduced (2026-10-17). `null` means that no source data is delivered for that job; it does **not** mean the job did no retrieval.

Read `answer_markdown` and `sources` together, from the same `completed` reply: that pair is the result.

Sources are built from the final answer, after the evidence review and any rewrite, not from the draft streamed while the answer was being written. A citation that the review removed from the answer is not listed. Every entry's `cited_as` is text that appears in `answer_markdown`. Nothing in an entry is generated: texts, dates, courts and links are only what retrieval returned, and a citation nothing retrieved has its content `null`.

**A listed source does not mean the answer's legal analysis is correct**, and it does not mean every citation was verified. Read `retrieval` on each entry, and see [Presenting evidence and sources](#presenting-evidence-and-sources).

Fields of every entry:

| Field | Type | Meaning |
|---|---|---|
| `kind` | string | `statute`, `judgment` or `interpretation` (a constitutional interpretation, 釋字第N號). |
| `cited_as` | string | The citation exactly as it is written in `answer_markdown`. Use it to find the citation in the answer. |
| `retrieval` | string | What this job obtained of the source; see the tables below. |
| `tool` | string \| null | The retrieval tool that returned it (`search_statutes`, `get_article`, `search_judgments`, `read_judgment`, …). `null` when nothing was retrieved. |
| `arguments` | object \| null | Identity only: `{"law", "article"}` for a statute, `{"court", "case_number"}` for a judgment. Search queries are never included. |
| `quote_not_found` | boolean \| null | The answer put a passage in quotation marks beside this source that is not in the text retrieved for it — for a statute, a passage given as the article's words with any sentence that is not in the retrieved article. `null` when nothing was retrieved to check a quote against (`retrieval` `not_retrieved` or `cited_in_retrieved_judgment`). |
| `cited_item_not_found` | string \| null | Statutes only: the 第N項 / 第N款 the answer cites that the retrieved article does not have (e.g. `"第2項"`), else `null`. |
| `quote_marked_as_gist` | boolean | Such a passage was turned into a paraphrase in the answer (「…」 → （意旨：…）). |

Statutes:

| `retrieval` | Meaning |
|---|---|
| `text` | The article was looked up by name (`get_article`) and its text returned. |
| `excerpt` | A search returned the article with a passage of its text. |
| `listed` | A search listed the article without text. |
| `not_retrieved` | The answer cites it, but this job's retrieval record does not show it was retrieved. Treat it as not confirmed by this job. |

| Statute field | Meaning |
|---|---|
| `law`, `article` | The act name and article number as retrieved (for example 「中華民國刑法」, 「第 277 條」). |
| `text` | The retrieved text, or `null`. |
| `text_truncated` | `true` when the retrieved passage was cut short (the upstream marks it with an ellipsis); the text is then **not** the full article. `null` when there is no text. |
| `url` | The official link the upstream returned: the law's page on the national law database, not a per-article page. `null` when none. |
| `version_date` | The version date the upstream returned, or `null`. |

Interpretations (`kind: "interpretation"`): `retrieval` is `read`, `excerpt`, `listed`, `cited_in_retrieved_judgment` (named inside a retrieved judgment, not itself retrieved) or `not_retrieved`; `number` (釋字第N號), `decision_date`, `excerpt`, `url` (the Constitutional Court's page) and `full_text` come from what was retrieved, and are `null` when nothing was. Fast lists the interpretations most relevant to each judgment search it makes; an interpretation the answer names that was not retrieved is `not_retrieved`.

Judgments:

| `retrieval` | Meaning |
|---|---|
| `read` | The judgment was opened (`read_judgment`). `full_text.complete` is `true` when all of it was read, `false` when only part was; `full_text` gives `chars_read` and `total_chars`. This says what the service read. The reply itself still carries only the search `excerpt` (or none), not the text that was read. |
| `excerpt` | A search returned the judgment with an excerpt only. |
| `listed` | A search listed the judgment without an excerpt. |
| `cited_in_retrieved_judgment` | Not retrieved itself; it is named inside the text of a judgment this job did retrieve. Content is `null`. |
| `not_retrieved` | The answer cites it, but this job's retrieval record does not show it was retrieved. Content is `null`. Treat it as not confirmed by this job. |

| Judgment field | Meaning |
|---|---|
| `court`, `case_number`, `decision_date` | As retrieved. |
| `excerpt` | The search excerpt, or `null`. The text read with `read_judgment` is not included. |
| `url` | The judgment's page on the Judicial Yuan's judgment system, as retrieved, or `null`. |
| `full_text` | `{"complete", "chars_read", "total_chars"}` for a read judgment, otherwise `null`. |

`sources_summary`:

| Field | Meaning |
|---|---|
| `cited` | Number of entries in `sources`. One source cited several times is one entry. |
| `by_retrieval` | Entries per `retrieval` value. |
| `omitted_from_answer` | Citations the evidence review took out of the answer (an unverified case number replaced by 「一則未經本次查核的裁判（字號從略）」). They are not in `sources`. |
| `not_in_answer` | Citations whose text is not in the delivered answer. They are not in `sources`. |
| `retrieved_not_cited` | `{"statutes", "judgments", "interpretations"}`: distinct retrieved results the answer does not cite. Only counted; they are not in `sources`. |

A completed reply observed live on 2026-10-17. `job_id` and `answer_markdown` are replaced, only three of the eight `sources` entries are kept, and their `text` / `excerpt` are shortened for this document. `text_truncated` describes the retrieved text, not this shortening:

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
  "draft_check": {
    "class": "A",
    "changes": 0
  },
  "sources": [
    {
      "kind": "statute",
      "cited_as": "刑法第277條",
      "retrieval": "text",
      "law": "中華民國刑法",
      "article": "第 277 條",
      "text": "傷害人之身體或健康者，處五年以下有期徒刑、拘役或五十萬元以下罰金。\r\n犯…",
      "text_truncated": false,
      "url": "https://law.moj.gov.tw/LawClass/LawAll.aspx?pcode=C0000001",
      "version_date": null,
      "tool": "get_article",
      "arguments": {
        "law": "中華民國刑法",
        "article": "第 277 條"
      },
      "quote_not_found": false,
      "quote_marked_as_gist": false
    },
    {
      "kind": "judgment",
      "cited_as": "臺灣高等法院臺中分院101年度上易字第350號",
      "retrieval": "excerpt",
      "court": "臺灣高等法院臺中分院",
      "case_number": "101年度上易字第350號",
      "decision_date": "2012-07-24",
      "excerpt": "[理由，推定為法院判斷] ⒈按「對於現在不法之侵害，而出於防衛自己或他人…",
      "url": "https://judgment.judicial.gov.tw/FJUD/data.aspx?ty=JD&id=TCHM%2C101%2C%E4%B8%8A%E6%98%93%2C350%2C20120724%2C1",
      "full_text": null,
      "tool": "search_judgments",
      "arguments": {
        "court": "臺灣高等法院臺中分院",
        "case_number": "101年度上易字第350號"
      },
      "quote_not_found": false,
      "quote_marked_as_gist": false
    },
    {
      "kind": "judgment",
      "cited_as": "最高法院87年度台上字第3720號",
      "retrieval": "cited_in_retrieved_judgment",
      "court": null,
      "case_number": null,
      "decision_date": null,
      "excerpt": null,
      "url": null,
      "full_text": null,
      "tool": null,
      "arguments": null,
      "quote_not_found": false,
      "quote_marked_as_gist": false
    }
  ],
  "sources_summary": {
    "cited": 8,
    "by_retrieval": {
      "excerpt": 5,
      "text": 1,
      "cited_in_retrieved_judgment": 2
    },
    "omitted_from_answer": 0,
    "not_in_answer": 0,
    "retrieved_not_cited": {
      "statutes": 8,
      "judgments": 2
    }
  },
  "artifacts": [
    {
      "name": "fast_answer",
      "ready": true
    }
  ]
}
```

A citation with nothing retrieved has this shape. This entry is illustrative, not a capture:

```json
{"kind": "statute", "cited_as": "民法第184條", "retrieval": "not_retrieved", "law": null, "article": null, "text": null,
 "text_truncated": null, "url": null, "version_date": null, "tool": null, "arguments": null,
 "quote_not_found": false, "quote_marked_as_gist": false}
```

Sources are stored with the job's result and are readable only by the identity that submitted the job (another identity gets `403 Forbidden`). They are not removed after one hour the way streamed events are.

Jobs and artifacts are scoped to the authenticated identity; another identity reading this job gets `403 Forbidden`.

---

## Synchronous lookups: `get_article`, `search_statutes`, `search_judgments`, `search_interpretations`, `read_judgment`

These five tools answer at once: they create no job, call no model and are not charged. They read the same statute and judgment sources Fast Legal's research reads, so an article read here is the same text Fast Legal works from. Measured on 2026-10-20: `get_article` about 0.4 s, `search_statutes` about 1.3 s, `search_judgments` about 1.8 s, `read_judgment` about 0.4–1 s.

**Errors.** A refusal is `{"ok": false, "error_code": ..., "message": ..., "context": {...}}`:

| `error_code` | Meaning | `context` |
|---|---|---|
| `NOT_FOUND` | The source has no such article or judgment. An answer about the sources, not a failure. | `reason`, and the article or case asked for |
| `INVALID_ARGUMENT` | The arguments cannot be used: an empty or over-long (120 characters) query, an unreadable article number, a `top_k` / `max_chars` out of range, `around` together with `offset`, a judgment named by neither `doc_id` nor `court` + `case_number`. | `field` when one argument is at fault, `reason` |
| `RETRIEVAL_FAILED` | The source failed this time; nothing is wrong with the request. Try again later. | none |

A search that matches nothing is `ok: true` with an empty `results` list. **Rate limit:** the MCP endpoint's per-caller limit (120 calls a minute) applies; there is no separate limit for these tools.

## `get_article`

Returns `law` (the act's full name; common short names such as 勞基法 are accepted), `article`, `text` (the whole article, paragraphs and items), `status` (`in-force` when current), `level` (法律 / 命令), `amended_on` (the last amendment date when the source gives one; currently `null`), `url` and `id`.

### Live description (verbatim)

```text
Read one statute article: the act's full name, the article number, its whole text (paragraphs and items), whether it is in force,
    its last amendment date when the source gives one (null otherwise), and a link and an identifier. Common short names are accepted
    (勞基法 → 勞動基準法). Synchronous: no job, no charge.

    Args:
        law: The act, e.g. 民法, 勞動基準法 or 勞基法.
        article: The article number only, e.g. 184, 第184條, 第一百八十四條 or 7-2.

    Errors: NOT_FOUND (no such article), INVALID_ARGUMENT (the article number cannot be read), RETRIEVAL_FAILED (the source failed).
    
```

### Exact input schema (verbatim)

```json
{
  "properties": {
    "law": {
      "title": "Law",
      "type": "string"
    },
    "article": {
      "title": "Article",
      "type": "string"
    }
  },
  "required": [
    "law",
    "article"
  ],
  "title": "get_articleArguments",
  "type": "object"
}
```

## `search_statutes`

Returns `results`, most relevant first, each with the fields of `get_article` and `score`. `law` keeps only results from that act; `level` (`law` / `order`) is applied by the source.

### Live description (verbatim)

```text
Search statute articles by relevance. Each result: the act, the article number, the text (or an excerpt), the relevance score and
    whether it is in force. Synchronous: no job, no charge.

    Args:
        query: Words a statute would use (法典的用語), e.g. 押金 租賃契約 返還; at most 120 characters.
        law: Only results from this act (full or common short name).
        level: law = acts only; order = administrative orders only; omitted = both.
        top_k: How many results, 1–30 (default 10).

    Errors: INVALID_ARGUMENT (an empty or over-long query, a bad top_k), RETRIEVAL_FAILED (the source failed). No match is an empty list.
    
```

### Exact input schema (verbatim)

```json
{
  "properties": {
    "query": {
      "title": "Query",
      "type": "string"
    },
    "law": {
      "anyOf": [
        {
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Law"
    },
    "level": {
      "anyOf": [
        {
          "enum": [
            "law",
            "order"
          ],
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Level"
    },
    "top_k": {
      "default": 10,
      "title": "Top K",
      "type": "integer"
    }
  },
  "required": [
    "query"
  ],
  "title": "search_statutesArguments",
  "type": "object"
}
```

## `search_judgments`

Returns `results`: `court`, `case_number`, `title`, `decision_date`, `passage` (the matching passage, with the source's section labels in brackets), `passage_at` (for `read_judgment` `around`), `roles` (those labels: 「理由，推定為法院判斷」 is the court's reasoning; 「未確認為法院判斷」 may be a party's argument), `doc_id`, `url`, `score`. `court` keeps only that court's judgments.

### Live description (verbatim)

```text
Search court judgments for how courts decide a point. Each result: the court, the case number, the decision date, the matching
    passage, its position (passage_at, for read_judgment's around) and the doc_id. roles lists the section labels the source puts on the
    passage — 「理由，推定為法院判斷」 is the court's own reasoning; 「未確認為法院判斷」 may be a party's argument. Synchronous: no job, no charge.

    Args:
        query: How a court's reasoning would put it, e.g. 共同正犯在合同意思範圍內; at most 120 characters.
        court: Only judgments of this court, e.g. 最高法院 (matched within the court's name).
        top_k: How many results, 1–20 (default 5).

    Errors: INVALID_ARGUMENT (an empty or over-long query, a bad top_k), RETRIEVAL_FAILED (the source failed). No match is an empty list.
    
```

### Exact input schema (verbatim)

```json
{
  "properties": {
    "query": {
      "title": "Query",
      "type": "string"
    },
    "court": {
      "anyOf": [
        {
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Court"
    },
    "top_k": {
      "default": 5,
      "title": "Top K",
      "type": "integer"
    }
  },
  "required": [
    "query"
  ],
  "title": "search_judgmentsArguments",
  "type": "object"
}
```

## `search_interpretations`

Searches the constitutional decisions: 司法院大法官解釋 (釋字第1號至第813號) and 憲法法庭判決 (憲判字). Returns `results`, most relevant first, and `source` (the attribution below). Each result:

| Field | Meaning |
|---|---|
| `doc_id` | Pass it to [`read_judgment`](#read_judgment) to read the full text, e.g. `JYIN,84,釋字,380,19950526`. |
| `citation` | 「司法院釋字第380號解釋」 / 「111年憲判字第8號判決」. |
| `case_number`, `decision_date`, `url`, `score` | As in `search_judgments`. |
| `passage` | The matching passage; each segment headed by its section — 【解釋爭點】 / 【解釋文】 / 【理由書】 for a 釋字; for a 憲判字 the judgment's own heading (主文, or e.g. 參、形成主文之法律上意見). Segments are separated by `\n…\n`. |
| `passage_sections` | The section of each segment, in order. |
| `passage_at` | The passage's position, for `read_judgment`'s `around`. |
| `standing` | `changed` — later changed or no longer applied by a 釋字 or 憲判字, wholly or in part; `supplemented` — supplemented and still in force; `none` — checked, and no later 釋字 or 憲判字 changed or supplemented it; `unknown` — no record (never reported as `none`). |
| `changed_by`, `supplemented_by` | Who changed / supplemented this one. |
| `changes` | What this decision itself changed or supplemented (earlier 釋字, or 院字 / 院解字 interpretations, whose `target_doc_id` is null). |
| `standing_checked_through` | The last decision the status was checked against. |

Each entry of `changed_by`, `supplemented_by` and `changes`: `by` (e.g. 111年憲判字第2號), `by_doc_id`, `target`, `target_doc_id`, `relation` (變更 / 不再援用 / 補充), `scope` (全部 / 部分; null when the decision does not say), and `evidence` — the later decision's own sentence, verbatim from its text (whitespace as in the source).

**How the change status is made.** A table built from the full texts of every 釋字 (第1號至第813號) and every 憲判字 in the source, by reading each sentence that names an interpretation together with 變更 / 不再援用 / 補充; not inferred by a model. On 2026-10-21, checked through 憲法法庭115年憲判字第7號判決 (2026-10-08), numbering complete for each year: 12 changed, 38 supplemented, 763 none among the 813 釋字. `standing_checked_through` on every result names the last judgment checked; a 釋字 or 憲判字 decided after it is `unknown`.

**How it is kept up to date.** The source is checked once a day for 憲判字 after the last one checked, in order, counting only a judgment whose full text is in the source; a missing number before a later one of the same year stops the check there. A new judgment with no sentence that names an interpretation together with 變更 / 不再援用 / 補充 is added at once and `standing_checked_through` moves past it. A new judgment with such a sentence is read and classified by a person first — it is not classified automatically — and until then the check stays before it, so a status that may have changed is not reported as `none` beyond what was read.

**Search coverage.** The 釋字 have their own index. The 憲判字 are found through the judgment index (all courts), so a 憲判字 appears when it is among the closest judgments for the query.

**Source.** 「出處：司法院釋字第1號至第813號解釋取自憲法法庭網站（cons.judicial.gov.tw）；憲法法庭判決取自司法院資料開放平臺（依該平臺授權條款註明出處）。變更狀態依上開全文整理，查核至憲法法庭115年憲判字第7號判決（2026-10-08）。」 — the `source` field of every result carries this text; the date it was checked through follows the table.

### Live description (verbatim)

```text
Search the constitutional decisions: 司法院大法官解釋 (釋字第1號至第813號) and 憲法法庭判決 (憲判字). Each result: doc_id (pass it to
    read_judgment), citation, case_number, decision_date, url, score, the matching passage with its section (解釋爭點 / 解釋文 / 理由書; for
    a 憲判字 主文 / 理由) and passage_at, and the change status: standing — changed (later changed or no longer applied, wholly or in part),
    supplemented (supplemented, still in force), none (checked, no later change or supplement), unknown (no record) — with changed_by,
    supplemented_by (who did it, with that decision's own sentence as evidence) and changes (what this one itself changed or supplemented).
    Read standing before relying on an interpretation: a changed one is not the law in that respect. Synchronous: no job, no charge.

    Args:
        query: A legal concept or how the decision would put it, e.g. 大學自治 學術自由 or 強制道歉 不表意自由; at most 120 characters.
        top_k: How many results, 1–8 (default 5).

    Errors: INVALID_ARGUMENT (an empty or over-long query, a bad top_k), RETRIEVAL_FAILED (the source failed). No match is an empty list.
    
```

### Exact input schema (verbatim)

```json
{
  "properties": {
    "query": {
      "title": "Query",
      "type": "string"
    },
    "top_k": {
      "default": 5,
      "title": "Top K",
      "type": "integer"
    }
  },
  "required": [
    "query"
  ],
  "title": "search_interpretationsArguments",
  "type": "object"
}
```

## `read_judgment`

Returns `disposition` (主文), `text` (one page, at most `max_chars`), `offset`, `next_offset` (null when nothing follows; pass it as `offset` to read on), `total_chars`, `cited_articles`, `court`, `case_number`, `decision_date`, `title`, `url` and `doc_id`.

A 司法院 釋字 (e.g. `court` 司法院, `case_number` 釋字第380號) or a 憲法法庭 憲判字 (e.g. 憲法法庭, 111年憲判字第8號) also carries its change status — `standing`, `changed_by`, `supplemented_by`, `changes`, `standing_checked_through` — and `source`, exactly as in [`search_interpretations`](#search_interpretations). Any other judgment is unchanged.

### Live description (verbatim)

```text
Read one judgment's original text, a page at a time: the 主文 (disposition) and the text from the start, from offset, or from around
    (a passage_at from search_judgments). next_offset is not null when more follows — pass it as offset to read on. Identify the judgment
    by doc_id (from search_judgments or search_interpretations), or by court and case_number (e.g. 最高法院 and 112年度台上字第123號;
    司法院 and 釋字第380號; 憲法法庭 and 111年憲判字第8號). A 釋字 or 憲判字 also carries its change status (standing, changed_by,
    supplemented_by, changes; see search_interpretations) and source. Synchronous: no job, no charge.

    Args:
        doc_id: The judgment's doc_id.
        court: The court, with case_number, when there is no doc_id.
        case_number: The case number, with court.
        around: Start from this passage position (search_judgments' passage_at). Not with offset.
        offset: Start from this character; the previous page's next_offset.
        max_chars: At most this many characters of text, 200–3000 (default 3000).

    Errors: NOT_FOUND (no such judgment), INVALID_ARGUMENT (neither doc_id nor court + case_number, around with offset, a bad number),
    RETRIEVAL_FAILED (the source failed).
    
```

### Exact input schema (verbatim)

```json
{
  "properties": {
    "doc_id": {
      "anyOf": [
        {
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Doc Id"
    },
    "court": {
      "anyOf": [
        {
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Court"
    },
    "case_number": {
      "anyOf": [
        {
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Case Number"
    },
    "around": {
      "anyOf": [
        {
          "type": "integer"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Around"
    },
    "offset": {
      "anyOf": [
        {
          "type": "integer"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Offset"
    },
    "max_chars": {
      "default": 3000,
      "title": "Max Chars",
      "type": "integer"
    }
  },
  "title": "read_judgmentArguments",
  "type": "object"
}
```
