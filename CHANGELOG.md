# Changelog

All notable changes to the public AurCounsel MCP interface documentation will be recorded here.

The format is inspired by Keep a Changelog. Version numbers in this repository describe the **public documentation/interface contract**, not private backend release identifiers.

## [0.1.0] - Unreleased

### 2026-10-26 — `search_rulings`

#### Added

- `search_rulings` (the `lookup` permission; synchronous, no charge): the Ministry of Finance's tax rulings (財政部各稅法令函釋) and annual amount announcements — each result with `document_number` (發文字號), `summary`, `tax`, `article`, `passage`, `url`, `score` and `source` (the attribution the licence requires). A ruling is not law. Live 2026-10-26 05:16 UTC.

### 2026-10-26 — lookup calls retained for quality maintenance

#### Changed

- The arguments of the lookup tools (`get_article`, `get_laws`, `search_statutes`, `search_judgments`, `search_interpretations`, `read_judgment`) and `fast_legal`, and a summary of what each call returned (result count, each result's identifiers and score), are retained on the service side for quality maintenance. Tool arguments and responses are unchanged. From 2026-10-26 05:12 UTC.

### 2026-10-25 — one more review type (設備維護保養)

#### Added

- `review_contract` `review_type` 設備維護保養 (設備使用方 / 維護廠商), at every level (`medium`, `high`, `large`); `get_capabilities` `review.review_types` lists all twenty-two. Live 2026-10-25 14:27 UTC.

### 2026-10-25 — review_type guidance

#### Changed

- `review_contract` description: when the contract is one of the listed types (judged by its content, not only its title), send `review_type` with one of that type's two parties as `represented_party`; otherwise do not send it. Live 2026-10-25 13:37 UTC.

### 2026-10-25 — review: one rule on every level

#### Changed

- `review_contract`: every level (`medium`, `high`, `large`) reviews any contract with the same parameters. `represented_party` (the party as the contract names it, or 甲方 / 乙方) and `client_instructions` are required on every level; with `review_type`, `represented_party` must be one of the type's two parties — it no longer defaults to the first. A `review_type` outside `get_capabilities` `review.review_types` is ignored at every level. `get_capabilities` `review` no longer lists `represented_party` values. Live 2026-10-25 13:27 UTC.

#### Removed

- `review_contract` arguments `contract_type_hint` and `requested_jurisdiction`, and the response fields `jurisdiction`, `represented_party_sent` and `contract_type_hint`. The review deliverables no longer carry internal reference markers.

### 2026-10-25 — review opinion: one issue list

#### Changed

- The review opinion (`review_comments`, `memo`) is one numbered list of issues under 「重要議題」. An issue not reflected in the revised contract ends with 「(此項未納入修訂稿,請評估是否修改。)」. Live 2026-10-25 13:19 UTC.

### 2026-10-25 — review: a represented party is required

#### Changed

- `review_contract` no longer accepts a neutral `represented_party` (`neutral`, `中立`, `雙方`, `both parties` …) at any level (`medium`, `high`, `large`): a review is always for one party of the contract. Such a call is refused with `INVALID_INPUT` (`context.field: "represented_party"`, `detail: "represented_party_neutral"`, `choices` 甲方 / 乙方) before anything is sent; no job is created. `get_capabilities` `review.represented_party` is now `["party_a", "party_b"]`. `draft_contract` is unchanged (neutral still drafts for both sides in balance). Live 2026-10-25 11:31 UTC.

#### Removed

- The neutral review at `high` and `large` (added earlier today).

### 2026-10-25 — one more review type (銷售代理・居間)

#### Added

- `review_contract` `review_type` 銷售代理・居間 (委託方 / 代理商), at every level (`medium`, `high`, `large`); `get_capabilities` `review.review_types` lists all twenty-one. Live 2026-10-25 11:04 UTC.

### 2026-10-25 — four more review types

#### Added

- `review_contract` `review_type` 不動產委託銷售 (委託人 / 不動產經紀業者), 資訊系統維運與代管服務 (服務使用方 / 服務提供方), 室內裝修工程承攬 (定作人 / 承攬人) and 交通事故損害賠償和解 (受害人 / 加害人), at every level (`medium`, `high`, `large`); `get_capabilities` `review.review_types` lists all twenty. Live 2026-10-25 10:31 UTC.

### 2026-10-25 — neutral at high and large

#### Added

- `review_contract` at `high` and `large`: `represented_party` may be neutral (`neutral`, `中立`, `both parties` …) — the contract is reviewed from both parties' neutral standpoint. Live 2026-10-25 06:28 UTC.

### 2026-10-25 — high and large review any contract

#### Changed

- `review_contract` at `high` and `large` reviews any contract type: send `represented_party` (the party as the contract names it, or 甲方 / 乙方) and `client_instructions`; `review_type` remains available for the types in `get_capabilities` `review.review_types`. Live 2026-10-25 06:07 UTC.

### 2026-10-24 — review types: either party

#### Changed

- **`get_capabilities` `review.review_types`**: each entry is now `{"type", "represented_parties": ["<party>", "<party>"]}` — the type's two parties. It replaces the single `represented_party`. Live 2026-10-24 03:13 UTC.
- **`review_contract` with `review_type`**: `represented_party` may be either party of the type (omitted: the first). Another party is refused with `INVALID_INPUT` (`detail: "not_a_party_of_review_type"`, `accepted`) where it was `fixed_by_review_type` (`expected`).

### 2026-10-24 — three more review types (勞動契約, 冷鏈運送, 保密協議)

#### Added

- `review_contract` `review_type` 勞動契約 (for 受僱人), 冷鏈運送 (for 託運人) and 保密協議 (a one-way non-disclosure agreement, for 接收方), at every level (`medium`, `high`, `large`); `get_capabilities` `review.review_types` lists all sixteen. Live 2026-10-24 03:02 UTC.

### 2026-10-23 — statute status: effective dates after promulgation

#### Fixed

- Status (`status`, `effective_note`) of articles promulgated with 「自公布日施行」: in force from the third day counting the day of promulgation (中央法規標準法第 13 條), not on the day itself. Live 2026-10-23 17:04 UTC.
- 「自公布後 N 年施行」 is now read like 「…個月後施行」 (the same day N years later): 資源循環推動法 第 14 條、第 38 條 (promulgated 2026-06-17, two years) now show `not-yet-effective` until 2028-06-17. Live 2026-10-23 17:04 UTC.

#### Documented

- Change events (not live yet) gain `effective_basis` (`official_date` / `statutory_rule` / `null`) and `effective_note`; the illustrative example is updated.

### 2026-10-23 — change events documented ahead (not live yet)

#### Documented

- [`list_law_changes` and `get_law_change`](docs/tools.md#change-events-list_law_changes-get_law_change-not-live-yet): event fields, types and behaviour, with an **illustrative** example (not a real event). The tools go live once an act changes in the official data after 2026-10-23; that date, and the switch to a real example, will be recorded here.

### 2026-10-23 — statutes: pcode on results, get_laws; full-text snapshots begin

#### Added

- `get_article` and `search_statutes`: each article result has `pcode`, the act's 法規代號 (`null` when the act is not on the national law database). Live 2026-10-23 16:52 UTC.
- New tool [`get_laws`](docs/tools.md#get_laws): 1–50 pcodes or act names (full, short or former names) → each act's pcode, current name, level, status, `amended_on` and `url`, or `found: false`. Live 2026-10-23 16:52 UTC. `tools/list` now has fourteen tools.
- Full-text snapshots of every act, taken by the daily rebuild from the 法務部 OpenAPI whenever an act changes; the first (all 11,803 acts) on 2026-10-23 16:52 UTC. Change events and the tools to read them follow when two snapshots of a changed act exist.

### 2026-10-23 — statute results: article_url

#### Added

- `get_article` and `search_statutes`: each article result has `article_url`, the article's own page on the national law database (`LawSingle.aspx?pcode=…&flno=…`), for acts and administrative orders; `null` when there is no single-article page (a whole-act result, an act not on the database, an article number that cannot be read as one article). `url` is unchanged: the whole act's page.

### 2026-10-23 — draft_summary: a reason for every suggested term; fixed headings

#### Fixed

- `draft_summary`, **建議的商業條件**: each point now gives its reason for the suggestion; it no longer carries a placeholder 「—— 理由。」 with no reason.
- `draft_summary`: the four section headings are always written the same way — `**起草重點**`, `**建議的商業條件**`, `**仍需您決定的事項**`, `**主要風險與注意事項**` — where some summaries had them without bold. The format is now described under [`draft_summary` format](docs/tools.md#draft_summary-format); a future change to it will be recorded here before it is deployed. Summaries of drafts made before are unchanged.

### 2026-10-23 — job outputs kept per customer; job_id is opaque

#### Changed

- A new review, draft, revision or comparison job's outputs are stored separately for each customer. Jobs submitted before keep their outputs and identifiers; `get_job`, `get_artifact` and downloads work for both.
- `job_id` is documented as an opaque string: store it and send it back as received, without parsing it or assuming its length or characters (it may contain `~`).

### 2026-10-23 — keys: permitted tools and prepaid balance

#### Added

- Per-key permitted tools: `tools/list` lists only the tools a key may use; any other tool returns `TOOL_NOT_PERMITTED` (`context.tool`). A change applies from the next request.
- Prepaid balance: a prepaid key whose balance is zero or below gets `QUOTA_EXCEEDED` (`context.balance_micros`) for a charged job (`high` / `large`); `medium`, the lookups and `get_job` / `get_artifact` keep working, and running jobs finish (see [Keys](docs/tools.md#keys-permitted-tools-and-prepaid-balance)).
- A disabled key is refused with HTTP 401, as an unknown one.

### 2026-10-23 — statute search: a new query waits for its rewrite; results fill top_k

#### Changed

- `search_statutes`: a new legal-concept or plain-language query waits for its rewrite to finish, up to 4.5 s, so one call gets the full result (most take 1–4 s); a query asked before still answers almost at once. `timed_out` now only when the rewrite takes longer than that; calling again a little later gives the full result.
- `search_statutes` fills `top_k` whatever `rewrite` says; with `level`, the rewrite's searches are also asked at that level. Fewer only when the source has no more. 我媽過世後發現她欠了卡債 with `level` `law` and `top_k` 10 now returns 10 articles on the first call.
- Measured over 55 test queries none asked before, `top_k` 20: article numbers p50 0.4 s; other queries p50 2.2 s, the slowest 4.5 s (5.0 s with `level`).

### 2026-10-23 — statute search: same query, same results; `rewrite` in the result

#### Added

- `search_statutes` result: `rewrite` — `applied`, `timed_out`, `not_applicable` or `failed` (see [`search_statutes`](docs/tools.md#search_statutes)).

#### Changed

- `search_statutes`: a query's rewrite and searches are kept until the daily rebuild changes the statute tables (or the service restarts), so the same query returns the same results all day. A rewrite that did not finish in time is completed in the background and used by the next call of the same query.

### 2026-10-23 — statute search: level ranks as without it; repealed after current

#### Changed

- `search_statutes` with `level`: ranked the same way as without `level`, then only that level kept; the same search at that level fills `top_k` if needed. 老闆不給加班費 with `level` `law` now has 勞動基準法第24條 first.
- `search_statutes`: unless the query names an act, repealed articles come after current ones.

### 2026-10-23 — statute search: level is rewritten too; results fill top_k

#### Changed

- `search_statutes` with `level`: a legal concept or plain-language query is rewritten as without `level`, and the results are only of that level (`law` = acts, `order` = administrative orders).
- `search_statutes` fills `top_k`: a plain-language query no longer returns only 1–2 articles; after the articles that match well come those that match less well, most relevant first. Fewer than `top_k` only when the source has no more.

### 2026-10-23 — statute search: legal concepts and plain language

#### Changed

- `search_statutes`: a query that is not an article number or an act's name (不當得利, 老闆不給加班費) is rewritten into the articles that decide it before searching; those articles, the headings of the acts and the query's own words are ranked together. Each suggested article is read from the source. Without an answer from the rewrite within about 2 s, the query is searched as before. Measured over 55 test queries: article numbers p50 0.40 s, other queries p50 1.9 s.
- The five synchronous lookups no longer all "call no model": `search_statutes` does for the rewrite above; the other four do not.

### 2026-10-23 — statute search: article numbers, short and former names, 且 / 或 / 排除, status; 釋字第804–813號 not provided

#### Added

- `search_statutes` reads an act and an article number (民法184, 民法第一百八十四條, 民法一八四, 刑法185-3, 民法第184條之1, 勞基法 84-1, 勞動基準法第9條第1項): the first result is that article, as `get_article` returns it. An article that does not exist is searched as words (no error). An act's name alone searches that act.
- `search_statutes` syntax: space or `&` / `＆` = and; `+` / `＋` = or; a leading `-` / `－` excludes results whose text or act name contains the word, applied before the list is cut to `top_k`.
- Statute results (`get_article`, `search_statutes`): `status` is `in-force`, `repealed`, `not-yet-effective` or `unknown`; `amended_on` is the act's last amendment date; `effective_note` when the act or the article's promulgated wording is not yet in force (民法第1223條). From 法務部全國法規資料庫 OpenAPI, rebuilt daily.
- Short and former names of acts (立法院開放資料 ID301, plus common short names such as 民訴, 刑訴, 行訴, 強執法, 國賠法, 家事法, 租賃條例): accepted by `get_article`, `search_statutes` and its `law`. 電腦處理個人資料保護法 → 個人資料保護法.

#### Changed

- Repealed acts are marked `repealed` (出版法, 動員戡亂時期臨時條款, 基本工資審議辦法 were `in-force`), and `search_statutes` returns them with that status rather than leaving them out.
- `search_statutes` `law` searches within that act instead of filtering a general search.
- `search_interpretations` covers 釋字第1號至第803號. 釋字第804號至第813號 are not provided (they are not on the official 司法院資料開放平臺): not returned, `read_judgment` `NOT_FOUND`, change records from them not shown (釋字第528號 `standing` `unknown`). The `source` text states the official sources.

### 2026-10-22 — draft notes: wrong citations corrected; `get_job` `note_check`

#### Added

- `get_job` `note_check` on a finished draft: `{checked, corrected, removed}` for the statute citations in `draft_summary`. `null` for other capabilities and for earlier drafts.

#### Changed

- `draft_summary`: a citation to the wrong article is now corrected to the article that says what the sentence says, rather than having its number removed. When a number is removed, the sentence is reworded so it does not point at a missing article (no leftover 「該條」 or 「同條」). Tables and quoted blocks keep their layout.

### 2026-10-22 — draft notes: statute citations checked; no summary line for a finished draft

#### Changed

- `draft_summary`: every statute article it cites (「<法規名>第 N 條」) is checked against the current article text before the file is written. A wrong number is corrected or removed, and a statutory term that contradicts the article is corrected. If a citation cannot be checked, its article number is removed and the law name is kept. The drafted contract itself is unchanged.
- `get_job` `summary.line` is `null` for a finished draft (it used to be a fixed sentence with no information).

### 2026-10-22 — three more review types (最高限額抵押, 會計師委任, 不動產附負擔贈與)

#### Added

- `review_contract` `review_type` 最高限額抵押 (for 抵押人), 會計師委任 (for 委任人) and 不動產附負擔贈與 (for 贈與人), at every level (`medium`, `high`, `large`); `get_capabilities` `review.review_types` lists all thirteen. `get_capabilities` example re-captured.

### 2026-10-22 — four more review types

#### Added

- `review_contract` `review_type` 合夥 (for 非執行業務合夥人), 收購意向書 (for 出售股東), 保證 (for 保證人) and 金錢借貸 (for 貸與人), at every level (`medium`, `high`, `large`); `get_capabilities` `review.review_types` lists all ten. `get_capabilities` example re-captured.

### 2026-10-21 — step-by-step progress for every job

#### Added

- `get_job` `after_seq` for `review`, `draft`, `revise` and `compare` (as `fast_legal`): `events` after that number and `last_seq`; each event `{seq, ts, type, step, text, detail?}` — step code, Chinese text, and what the job is on (a count, or the clause number and heading being worked on), ending with `done`.
- `progress.text`: the current step in Chinese, on every `get_job` reply.
- docs/job-lifecycle.md: the complete stage list of each capability (code, Chinese name, fraction), per path.

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
