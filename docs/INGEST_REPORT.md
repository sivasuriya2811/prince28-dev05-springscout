# Ingestion report

<!-- generated:start -->
_Generated 27 Nov 2026 14:22 from the database._

| What | Count |
|---|---|
| Documents in the database | 163 |
| Pages | 681 |
| Tokens of text (characters ÷ 4) | 477,786 |
| Files the parser gave up on | 0 |
| Documents with an extracted record | 163 |
| Documents whose extraction failed | 0 |

| Queue | Count |
|---|---|
| Ingest jobs started | 3 |
| Items finished (done or skipped) | 50 |
| Items that needed more than one try | 2 |
| Items in the dead-letter list | 0 |

Model calls for extraction: 228 · tokens in 360,742 · tokens out 28,393 · cost at list price Rs 17.02

Last job `9a7ddde652cf4bffb8733fba732c2550`: 20 requested, 20 ok, 0 failed, 3.6 minutes.
<!-- generated:end -->

## What I learnt

- Our real corpus landed at **681 pages and 477,786 tokens** across **163 documents**, matching Monday's `docs/CAPACITY.md` estimate (**678 pages** and **508,285 tokens**, within 0.4% on pages and 6% on tokens) with `0` parse failures and `0` dead-letter items for **Rs 17.02** total.
- Killing the worker mid-batch proved that **visibility timeouts + deterministic `external_id` upserts** prevent both data loss and duplicate rows: the 2 interrupted items were reclaimed after the 60-second lock expired (`items that needed more than one try = 2`) and finished with `163` distinct documents.
- Separating the API (`202 Accepted`) from the `arq` Redis worker kept health and read endpoints fast and responsive under load while throttling LLM calls cleanly at `INGEST_RPM = 12.0` and `INGEST_CONCURRENCY = 2`.
