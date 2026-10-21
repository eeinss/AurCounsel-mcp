# Changelog

All notable changes to the public AurCounsel MCP interface documentation will be recorded here.

The format is inspired by Keep a Changelog. Version numbers in this repository describe the **public documentation/interface contract**, not private backend release identifiers.

## [0.1.0] - Unreleased

### 2026-10-21 — three more review types

#### Added

- `review_contract` `review_type` 經銷 (for 經銷商), 買賣 (for 買受人) and 軟體開發委託 (for 委託方), at every level (`medium`, `high`, `large`); `get_capabilities` `review.review_types` lists all six. `get_capabilities` example re-captured.

### 2026-10-21 — review at `high` and `large` for three contract types

#### Added

- `review_contract` `review_type` (住宅租賃 / 國外團體旅遊 / 搬家服務, listed in `get_capabilities` `review.review_types` with each type's represented party) and `client_instructions`: the type-specific review, at any level.
- `review_contract` `model` `high` and `large` are open, for those `review_type`s only; charged by usage like a `high` / `large` draft. Without `review_type` they are refused with `INVALID_INPUT` (`detail: model_not_open_for_review_type`, `open_review_types`). `medium` is unchanged.

### 2026-10-21 — interpretation change status kept up to date; source wording

#### Changed

- The change status of 釋字 and 憲判字 is checked daily against new 憲判字: a judgment with no sentence that could change or supplement an interpretation is added automatically; one with such a sentence is read by a person before the status moves past it. `standing_checked_through` always names the last judgment checked.
- `source` now reads 「出處：司法院釋字第1號至第813號解釋取自憲法法庭網站（cons.judicial.gov.tw）；憲法法庭判決取自司法院資料開放平臺（依該平臺授權條款註明出處）。變更狀態依上開全文整理，查核至…」.

### 2026-10-21 — `search_interpretations`; the change status of 釋字 and 憲判字

#### Added

- `search_interpretations` (synchronous, free): 司法院釋字第1號至第813號 and 憲法法庭憲判字, each result with its section (解釋爭點 / 解釋文 / 理由書; a 憲判字's own heading), a `doc_id` for `read_judgment`, and its change status.
- Change status (`standing`: changed / supplemented / none / unknown, with `changed_by`, `supplemented_by`, `changes`, each carrying the later decision's own sentence as `evidence`) on `search_interpretations` results and on a 釋字 or 憲判字 read with `read_judgment`. Checked through 憲法法庭憲法法庭115年憲判字第7號判決 (2026-10-08); `source` names where the texts come from.

### 2026-10-20 — 經銷, 動產買賣 and 軟體開發委託 open at every level

#### Changed

- 經銷 (`distribution`), 動產買賣(採購 / 供貨) (`purchase`) and 軟體開發委託 (`sw_dev`) are on the one contract-type list (`draft.<level>.contract_types`): `high` and `large` now draft them with their minimum-content guidance instead of refusing them; `medium` is unchanged. Medical software development stays 醫療軟體開發委託.

#### Removed

- `draft.default_floor_types` and `draft.default_floor_models` in `get_capabilities` — those types are now listed under `draft.<level>.contract_types`. `get_capabilities` example re-captured.

### 2026-10-20 — 銷售代理・居間(招攬客戶) added to the Draft contract-type list

#### Added

- 銷售代理・居間(招攬客戶) (`agency`): the agent solicits customers for the principal, the principal contracts with each customer directly, and the agent is paid a commission without buying, reselling or holding stock — a sales agency (代辦商) or a brokerage (居間), representing the principal. A distributorship (經銷), a bare 代理 / 代理商, real property, shares, licences, consignment sales (代銷), leases, franchises, and marriage, insurance, securities, investment or labour brokerage are not this type. `get_capabilities` example re-captured.

### 2026-10-20 — 醫療軟體開發委託 added; 合資 limited to companies limited by shares

#### Added

- 醫療軟體開發委託 (`sw_dev_medical`, custom software development in a medical setting — a hospital, clinic, outpatient registration, medical records, a medical device, a pharmacy, long-term care, dentistry or health checks — representing the commissioning party) joins the contract types every open Draft level drafts with minimum-content guidance. A software-development contract in such a setting is drafted with this type's guidance at every level, the default included; one without it is unchanged.

#### Changed

- 合資 (`joint_venture`) applies to a joint venture forming a company limited by shares (股份有限公司); one forming a 有限公司 is no longer drafted with this type's guidance.

### 2026-10-20 — 不動產委託銷售 and 合資 added to the Draft contract-type list

#### Added

- 不動產委託銷售 (`brokerage_re`, an owner's brokerage listing of real property, representing the owner) and 合資(共同設立股份有限公司) (`joint_venture`, a joint venture forming a company limited by shares, representing one venturer) join the contract types every open Draft level drafts with minimum-content guidance. `get_capabilities` lists them in `draft.<level>.contract_types`; the example in docs/tools.md is re-captured.

### 2026-10-20 — model is a level; four lookup tools

#### Changed

- `model` (draft_contract, review_contract, compare_contracts, revise_contract) is a level: `medium` (the default; local, free), `high` or `large`. The earlier model names are no longer accepted (`INVALID_INPUT`, `context.accepted` lists the levels). `get_capabilities` reports levels: `models` lists `medium` / `high` / `large` without model ids; `capabilities.<capability>.default_model` is `medium`; `models` / `implemented_models` and the per-level sections (`draft.medium`, `draft.high`, `draft.large`, `review.<level>`) use level names; `draft.default_floor_models` is `["medium"]`. A submission's `model` echo is the level. This changelog's earlier entries are rewritten in level names.

#### Added

- `get_article`, `search_statutes`, `search_judgments`, `read_judgment`: synchronous statute and judgment lookups — no job, no charge, the same sources Fast Legal reads. Errors: `NOT_FOUND`, `INVALID_ARGUMENT`, `RETRIEVAL_FAILED` (see docs/tools.md).

### 2026-10-20 — fast_legal names no model

#### Changed

- The `fast_legal` description, its `level` documentation and the earlier changelog entries describe the levels without naming any model: `medium` is free and the fastest; `high` is charged by usage; `large` is charged by usage and researches the most deeply. The live description in docs/tools.md is updated verbatim.

### 2026-10-20 — 不動產附負擔贈與 and 設備維護保養 added to the Draft contract-type list

#### Added

- 不動產附負擔贈與 (`gift`, a gift of real property subject to a burden, representing the donor) and 設備維護保養 (`equip_maint`, annual maintenance of physical equipment at the user's site, representing the equipment user) join the contract types every open Draft model drafts with minimum-content guidance. `get_capabilities` lists them in `draft.<model>.contract_types` for `medium`, `large` and `high`; the examples in docs/tools.md show the nine-type list.

### 2026-10-20 — fast_legal levels medium / high / large

#### Changed

- `fast_legal(question, level)`: `level` is `"medium"` (default; free, the fastest), `"high"` or `"large"` (the deepest research). `high` and `large` are charged by usage. Any other value → `INVALID_INPUT` with `context: {"field": "level"}`.
- `get_job` for a `fast_legal` job at `high` or `large`: `cost_status` is `not_final` while processing and `settled` once the job is `completed` or `failed`, with `cost: {amount_micros, currency: "USD", final: true}` (a failed job is settled at 0). `answer_markdown` remains the answer alone; read the charge from `cost`.
- The live `fast_legal` description and input schema (`level` enum) in docs/tools.md are updated verbatim.

### 2026-10-20 — legal_research retired; fast_legal levels

#### Removed

- `legal_research` (Legal Research, the deeper research capability) is retired. It is no longer listed by `tools/list` (which now returns eight tools), and a call returns "Unknown tool". `get_job` / `get_artifact` no longer serve `legal_research` jobs, and its `research` artifact is gone. Its sections, examples and the advice to follow `fast_legal` with `legal_research` are removed from the README, quickstart, tools, artifacts, job lifecycle, errors and curl examples.
- `evidence.deep_research_recommended` is removed from `fast_legal` results. `evidence` now has exactly `status` (`COMPLETE` | `INSUFFICIENT_EVIDENCE`), `insufficiency_reason` and `review_outcome`.

#### Added

- `fast_legal(question, level)`: optional `level`, `"medium"` (default; AurCounsel's local model, no charge) or `"high"` (charged by usage). Any other value → `INVALID_INPUT` with `context: {"field": "level"}`.
- `get_job` for a `fast_legal` job returns `level` and `cost` / `cost_status`: for `high`, `cost_status` is `not_final` while processing and `settled` once the job is `completed` or `failed`, with `cost: {amount_micros, currency: "USD", final: true}` (a failed job is settled at 0); for `medium`, `cost` is `null` and `cost_status` is `unsupported`. `answer_markdown` is the answer alone and carries no cost line.
- A failed `fast_legal` job is documented with its `failure.error_code` (`RETRIEVAL_FAILED` / `FAST_UNAVAILABLE`), as the live description states; the earlier "no `failure` block" statement is removed.
- `fast_legal` description and input schema, `get_job` description (settled capabilities now include `fast_legal` at level `high`) and the cost support matrix updated.

### 2026-10-20 — Fast Legal: no evidence-status line in the answer; interim marker withdrawn

#### Changed

- A Fast Legal answer no longer ends with an evidence-status line; `evidence` is unchanged as a structured field.
- `evidence.status` is the answer review's own result. The interim rule (every answer `INSUFFICIENT_EVIDENCE` with the fixed "unverified" reason) is withdrawn.
- Citations the answer made without having retrieved them are looked up before delivery and kept, corrected or removed.

### 2026-10-20 — Fast Legal: constitutional interpretations

#### Added

- Fast Legal searches the constitutional interpretations (釋字 1–813) alongside its judgment searches; a cited 釋字第N號 appears in `sources` with `kind: "interpretation"`, its number, date and link, or as `not_retrieved` when nothing retrieved it.
- `sources_summary.retrieved_not_cited.interpretations`.

### 2026-10-19 — Fast Legal sources: statute quotes and 項 / 款 checked

#### Changed

- `sources[].quote_not_found` now also checks a passage the answer gives as a retrieved statute's words, sentence by sentence; it is `null` when nothing was retrieved to check against.
- A quotation beside an unretrieved statute is no longer rewritten as （未查證，轉述：…）.

#### Added

- `sources[].cited_item_not_found` (statutes): a cited 第N項 / 第N款 the retrieved article does not have.

### 2026-10-19 — 交通事故損害賠償和解 added to the Draft contract-type list

#### Added

- 交通事故損害賠償和解 (settlement of traffic-accident damages) joins the contract types every open Draft model drafts with minimum-content guidance (`get_capabilities` `draft.<model>.contract_types`).

### 2026-10-19 — three contract types added to the Draft contract-type list

#### Added

- 冷藏食品配送運送 (refrigerated food delivery carriage), 會計師委任 (engagement of a CPA) and 資訊系統維運與代管服務 (IT operations and hosting services) join the contract types every open Draft model drafts with minimum-content guidance (`get_capabilities` `draft.<model>.contract_types`).

### 2026-10-18 — 金錢借貸 added to the Draft contract-type list

#### Added

- 金錢借貸 (money loan) joins the contract types every open Draft model drafts with minimum-content guidance (`get_capabilities` `draft.<model>.contract_types`).

### 2026-10-18 — one contract-type list for every Draft model

#### Changed

- The contract types with minimum-content guidance are one list shared by every open Draft model (`get_capabilities` `draft.<model>.contract_types` is identical for each); the default model also drafts them with that guidance.
- A further local drafting option was built but not open for `draft_contract` (`PERMISSION_DENIED`); it is no longer offered.

### 2026-10-18 — `draft_contract` on `high` open

#### Added

- `draft_contract` with `model: "high"` is open for the contract types `get_capabilities` lists under `draft.high.contract_types` (now 室內裝修工程承攬 and 僱傭); other types are refused with `INVALID_INPUT`, never switched to another model. `high` drafts are settled in `get_job` `cost`.

### 2026-10-18 — `high` model, per-level status

#### Added

- `model: "high"` is built for `draft_contract` and `review_contract` and not open (`PERMISSION_DENIED`).
- `get_capabilities`: `capabilities.<capability>.models` = levels open now, `implemented_models` = levels built; per level `{"enabled": true|false}`; `draft.large` / `draft.high` also carry `contract_types` (open now), `jurisdiction`, `represented_party`.

#### Changed

- `review_contract` with `model` `large` or `high` returns `PERMISSION_DENIED` (was `INVALID_INPUT` for `large`).
- `draft_contract` with a model that does not draft the contract type returns `INVALID_INPUT` (`detail: model_not_open_for_contract_type`), was `UPSTREAM_REJECTED` 400.

### 2026-10-18 — cost wording

#### Changed

- `cost` is documented as the amount the job is settled at; the documentation no longer describes how it is computed. Verbatim `get_job` description re-captured.

### 2026-10-18 — `get_capabilities`, `review_contract` `model`, compare / revise closed

#### Added

- `review_contract` accepts `model`, limited to the models `get_capabilities` offers — now only the default; the `large` review is implemented but not open (`model: "large"` → `INVALID_INPUT`).
- `draft_contract` with `model: "large"` also accepts 僱傭 (employment) contracts.
- `get_capabilities` (read-only): open capabilities, accepted levels, contract types per level — read from the service's capability table.
- Error code `PERMISSION_DENIED` — capability not open; nothing sent, no job.
- `revise_contract` is registered again but not open.

#### Changed

- `compare_contracts` is closed: every call returns `PERMISSION_DENIED`.
- A job interrupted by a service restart is settled at 0 (`cost_status: settled`).
- `draft_contract` `represented_party` description no longer says it can be omitted for a neutral draft. Verbatim descriptions and schemas re-captured.

### 2026-10-18 — job cost

#### Added

- `get_job` returns `cost_status` (`settled` / `not_final` / `unsupported`) and, when settled, `cost: {amount_micros, currency: "USD", final: true}`. The amount is the amount the job is settled at, fixed when the job ends. Failed jobs are settled at 0. Supported now: `draft_contract` with `model: "large"`; all other capabilities / models report `unsupported`. Verbatim `get_job` description re-captured.

### 2026-10-18 — `draft_contract`: `large`, required jurisdiction

#### Added

- `draft_contract` accepts `model: "large"`. It is available only for 室內裝修工程承攬 (interior fit-out works) contracts under Taiwan law with a represented side; any other type is refused before a job exists (`UPSTREAM_REJECTED`, `upstream_status` 400) and is never switched to another model. Omitting `model` behaves as before (`medium`).
- Error code `MISSING_FIELD` (`context.field` names the field). `draft_contract` without `requested_jurisdiction` returns it, with nothing sent.

#### Changed

- `requested_jurisdiction` is documented as required for every draft (it was described as a deployment property); `represented_party` stays required for a contract draft. Verbatim `draft_contract` description and schema re-captured.

### 2026-10-17 — presenting evidence and sources

#### Changed

- Clients are no longer asked to display `evidence.status` and its reason next to the answer. The answer is the main content; `evidence` is supporting status information. The fixed interim `INSUFFICIENT_EVIDENCE` marker is a transitional label, not an assessment of the individual answer, and may be left out of the main answer area. Genuine insufficiency, failures and other concrete limitations must still not be presented as verified. Legal sources are presented from `sources`. New section: [Presenting evidence and sources](docs/tools.md#presenting-evidence-and-sources). No API change.

### 2026-10-17 — `fast_legal` sources

#### Added

- A completed `fast_legal` job's `get_job` reply carries `sources`: the statutes and judgments the final answer cites. Each entry has `cited_as`, `retrieval` (statute: `text` / `excerpt` / `listed` / `not_retrieved`; judgment: `read` with `full_text.complete` / `excerpt` / `listed` / `cited_in_retrieved_judgment` / `not_retrieved`) and the retrieved identity, text, link and date; `text_truncated` marks a cut statute text. The reply also carries `sources_summary`, which counts them and the retrieved results not cited. Jobs from before this change have `null`. Verbatim `get_job` description re-captured.

### 2026-10-17 — `fast_legal` progress and incremental answer

#### Added

- `get_job` takes an optional `after_seq`. On a `fast_legal` job the reply adds `events` (progress steps, the answer text while it is written, and a final `done`) after that sequence number, plus `last_seq`. Repeated polls repeat nothing. Events are kept for one hour after the job ends; the sweep runs about every 15 minutes. Verbatim description and schema re-captured.
- `fast_legal` `get_job` replies carry `draft_check` (`A` / `B` / `C`) on a completed job: how the answer differs from the draft streamed while it was written.

#### Changed

- `fast_legal` `progress` while `processing` is the job's current step (`{"step", "text"}`) instead of one fixed value.
- Corrected the interim evidence description: a genuinely insufficient answer keeps its own `insufficiency_reason` and has `deep_research_recommended: true`. Only answers carrying the fixed interim marker have the "unverified" reason and `false`. `evidence.status` is not, on its own, a legal verification result.

#### Unchanged

- A client that does not send `after_seq` gets the same reply as before, apart from the two additive fields above. There is still no cancel operation and no sources list.

### 2026-10-17 — documentation brought in line with the live server

#### Removed

- `revise_contract` has been withdrawn from the server and is no longer in `tools/list` (calling it returns `Unknown tool`). `tools/list` returns seven tools. Revision jobs submitted before the withdrawal can still be read with `get_job` / `get_artifact`; the docs keep that read-side guidance and drop the submission guidance.

#### Changed

- `draft_contract`: `represented_party` is required for a contract (no `doc_type`); a contract draft without it is refused with `INVALID_INPUT`. The live description still ends with "Omit to draft neutrally" — that sentence is out of date; send `neutral` instead. New optional argument `model`. Verbatim description and schema re-captured.
- `compare_contracts`: documents may also be sent by reference, `file_a_ref` + `file_b_ref`, instead of `file_a_b64` + `file_b_b64` (both sides the same way). Only `file_a_name` and `file_b_name` are schema-required. Verbatim description and schema re-captured.
- `get_job` / `get_artifact`: verbatim descriptions re-captured (they now describe `revise` jobs and their artifacts). The `context.accepted` artifact vocabulary has thirteen names (adds `redline_docx`).
- `fast_legal`: documented the interim rule — every delivered answer is currently `INSUFFICIENT_EVIDENCE` with an "unverified" `insufficiency_reason` and `deep_research_recommended: false`; the notice is not inside `answer_markdown`, so clients must render `evidence`. Clients should decide on `legal_research` from `evidence.status`, not from `deep_research_recommended`.
- Failed `fast_legal` / `legal_research` jobs carry no `failure` block and no reason.

#### Added

- `/upload`: how to obtain a `file_ref` (raw bytes in, `file_ref` out; one hour; owner-only; revocable; 50 MB; HTTP statuses).
- Rate limiting: 120 requests per client IP per 60 seconds; `429 Too Many Requests` with `Retry-After: 60`.
- Entitlements: a submission the token is not entitled to returns `UPSTREAM_REJECTED` with `context.upstream_status: 403`.
- Error codes: `EMPTY_FILE`, `FILE_TOO_LARGE`, `UNSUPPORTED_FILE_TYPE`, `INVALID_FILE_PAYLOAD`, `FILE_REF_NOT_USABLE`, `ARTIFACT_TOO_LARGE` (text artifacts over 8 MB are served by URL only), `UPSTREAM_REJECTED`, `UPSTREAM_ERROR`, `UPSTREAM_UNREACHABLE`.
- Retry guidance: submissions are not idempotent (re-sending creates a second job); there is no cancel operation.

### Added

- `fast_legal` tool (Fast Legal): bounded legal research with an evidence-sufficiency status (`COMPLETE` / `INSUFFICIENT_EVIDENCE`, model-assessed). Poll `get_job` for `answer_markdown` and `evidence`, or read `get_artifact(job_id, "fast_answer")`. Independent of `legal_research`: it never calls it, and the caller decides whether to follow up with `legal_research`. Documented in README, quickstart, tools, job lifecycle and curl examples.
- `legal_research` tool (Legal Research): submit a legal question, poll `get_job`, read `research_markdown` or `get_artifact(job_id, "research")`. Documented in README, quickstart, tools, job lifecycle and curl examples.

### Changed

- `review_contract`: `represented_party` is required. A call without it is refused with `INVALID_INPUT` and a readable message before anything is sent; there is no automatic party detection. Docs and schema capture updated to the live server.
- Authentication is required: every MCP request, including artifact downloads, must carry `Authorization: Bearer <AURCOUNSEL_MCP_TOKEN>`. Missing or invalid token: `401 Unauthorized`.
- Jobs and artifacts are scoped to the authenticated identity; reading another identity's job or artifact returns `403 Forbidden`. A job or artifact identifier alone does not grant access.
- README, quickstart, curl, Python and client-configuration examples updated to send the bearer header from `$AURCOUNSEL_MCP_TOKEN`; errors and artifacts pages document `401` / `403`.

### Added

- Initial public repository information architecture.
- Public AurCounsel MCP endpoint documentation.
- Documentation for the primary tools:
  - `review_contract`
  - `draft_contract`
  - `compare_contracts`
  - `get_job`
  - `get_artifact`
- Public asynchronous job lifecycle with:
  - `submitted`
  - `processing`
  - `completed`
  - `failed`
  - `unknown`
- Explicit terminal-failure semantics: partial/generated internal artifacts are not completed deliverables.
- Quickstart, architecture, artifact, error, security, and example documentation.
- Machine-truth verification markers for live schemas, response shapes, artifact vocabulary, authentication, and executable examples.
- MIT license for the contents of this repository.
- Security policy naming GitHub private vulnerability reporting as the channel for vulnerability reports.

### Verified against the live endpoint

- Exact descriptions and JSON input schemas for all five tools, from a live `tools/list`.
- Transport contract: JSON-RPC 2.0 over POST, protocol version `2025-06-18`, dual `Accept` requirement, SSE response framing, no session header, and the edge network's rejection of some user agents.
- `get_job` response shape, canonical status field, and the `completed`, `processing`, and `failed` bodies.
- One authorised `review_contract` submission of a synthetic contract, followed from submission to `completed`: the success-response shape, the `job_id` field path, ten `get_job` reads, and the observed `progress` stages.
- The twelve-value artifact vocabulary, taken verbatim from the server's own `context.accepted`.
- `get_artifact` response shape for available text artifacts, binary artifacts, and a terminally failed job. The bodies published in [artifacts.md](docs/artifacts.md) are sanitized examples in that verified shape — identifiers, URLs, and document content are placeholders — not verbatim captures.
- Error envelopes at all three layers: transport, tool execution, and application.
- Authentication state: none enforced at the MCP endpoint at the time of that capture (superseded: a bearer token is now required — see Changed above).
- `serverInfo.name` is `legalos` on the live deployment. That is the server identifier returned on the wire — a compatibility identifier for clients that key off `serverInfo.name` — and it is reproduced here unchanged. The product documented by this repository is AurCounsel; server-emitted strings are never rewritten, and this repository's own prose says AurCounsel throughout.
- `examples/curl.md` and `examples/python_client.py`, both executed as written.

### Pending verification before publication

- **PENDING_AUTH** — `draft_contract` and `compare_contracts` write to production and were never called: their success-response shapes, the six draft/compare artifact media types, and the `PARTY_CONFIRMATION_REQUIRED` refusal. The `review_contract` submission that was authorised does not establish these by analogy.
- **UNRESOLVED** — a `get_job` reading of `submitted` (the status appeared only in the submission response), `unknown` status behavior, failure detail beyond `JOB_FAILED`, the full progress-stage vocabulary, the transition set, rate limits and retry hints, artifact-URL access control, and the two client configuration file formats.
- The `get_artifact` response bodies in [artifacts.md](docs/artifacts.md) are sanitized examples in the verified live shape, not verbatim captures. The `failed` `get_job` body uses a placeholder identifier for the same reason.
