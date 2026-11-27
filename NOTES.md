# Engineering notes: SpringScout

## D03 · PostgreSQL

### Migrations (upgrade, downgrade, upgrade)

INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
INFO  [alembic.runtime.migration] Will assume transactional DDL.
INFO  [alembic.runtime.migration] Running downgrade b34d843e66d8 -> baac452f6a22, add gin index on metadata
INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
INFO  [alembic.runtime.migration] Will assume transactional DDL.
baac452f6a22
INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
INFO  [alembic.runtime.migration] Will assume transactional DDL.
INFO  [alembic.runtime.migration] Running upgrade baac452f6a22 -> b34d843e66d8, add gin index on metadata
baac452f6a22 -> b34d843e66d8 (head), add gin index on metadata
<base> -> baac452f6a22, create documents and pages


### The loader is idempotent


(springscout) PS C:\Users\S SIVA SURIYA\prince28-dev05-springscout> uv run python scripts/load_db.py
>> uv run python scripts/load_db.py
records=20 inserted=0 updated=0 unchanged=20
records=20 inserted=0 updated=0 unchanged=20


(springscout) PS C:\Users\S SIVA SURIYA\prince28-dev05-springscout> uv run python scripts/load_db.py
>> uv run python scripts/load_db.py
records=20 inserted=0 updated=0 unchanged=20
records=20 inserted=0 updated=0 unchanged=20


(springscout) PS C:\Users\S SIVA SURIYA\prince28-dev05-springscout> uv run python scripts/load_db.py
>> uv run python scripts/load_db.py
records=20 inserted=0 updated=1 unchanged=19
records=20 inserted=0 updated=0 unchanged=20



### EXPLAIN for ?page=Application Properties - Data Properties

```text
(springscout) PS C:\(\Users\S\) SIVA SURIYA\prince28-dev05-springscout> uv run python scripts/explain.py page "Application Properties - Data Properties"

-- 1) What the planner chooses on its own:
Seq Scan on documents  (cost=0.00..11.00 rows=1 width=36) (actual time=0.869..1.407 rows=2.00 loops=1)
  Filter: (metadata @> '{"page": "Application Properties - Data Properties"}'::jsonb)
  Rows Removed by Filter: 19
  Buffers: shared read=2 dirtied=2
Planning:
  Buffers: shared hit=143 read=8 dirtied=1
  Planning Time: 185.901 ms
  Execution Time: 1.460 ms

-- 2) Seq scan switched off, to prove the index can be used:
Bitmap Heap Scan on documents  (cost=12.81..16.82 rows=1 width=36) (actual time=1.803..1.805 rows=2.00 loops=1)
  Recheck Cond: (metadata @> '{"page": "Application Properties - Data Properties"}'::jsonb)
  Heap Blocks: exact=1
  Buffers: shared hit=2 read=2
  ->  Bitmap Index Scan on ix_documents_metadata_gin  (cost=0.00..12.81 rows=1 width=0) (actual time=1.770..1.770 rows=2.00 loops=1)
        Index Cond: (metadata @> '{"page": "Application Properties - Data Properties"}'::jsonb)
        Index Searches: 1
        Buffers: shared hit=1 read=2
Planning:
  Buffers: shared hit=1
  Planning Time: 0.082 ms
  Execution Time: 1.851 ms
```

Why did the planner choose a Seq Scan on my table? (2 lines, your own words)
The table currently only has 20 rows, which fit into just a couple of disk pages. Reading the whole table sequentially in one pass is cheaper and faster than loading the GIN index pages first and then jumping back to the heap table.

When would it switch to the GIN index? (1 line)
It will switch to the GIN index once the table grows large enough (hundreds or thousands of rows) that scanning every row costs more I/O than looking up selective keys in the index.





## D04 · Docker, Compose and tests

### The image

docker images springscout:dev
docker run --rm springscout:dev id


- Size: ___ MB (target: under 400 MB)
- First build: ___ s. After changing one line of code: ___ s.
- Which step said CACHED, and why? (1 line, your own words)
The dependency installation steps (COPY pyproject.toml uv.lock and uv sync) were CACHED because those lockfiles didn't change, so Docker skipped reinstalling packages and only rebuilt the source code layer

### The stack

records=20 inserted=20 updated=0 unchanged=0
records=20 inserted=0 updated=0 unchanged=20


### Breaking the database on purpose


db stopped:  /health → {"status":"ok","app":"springscout","env":"local"}
db stopped:  /ready  → {"status":"not_ready","checks":{"database":false}}
db started:  /ready  → {"status":"ready","checks":{"database":true}}


Why should a load balancer stop sending traffic here but not restart the app? (2 lines)
/ready is failing because the external database is down, so the load balancer should stop routing user traffic here until Postgres recovers. However, /health is still "ok", meaning the API process itself isn't crashed—restarting the app container wouldn't fix the database and would only waste resources

### Tests and coverage

(springscout) PS C:\Users\S SIVA SURIYA\prince28-dev05-springscout> uv run poe test
>> uv run poe cov
>>
Poe => pytest tests/unit
................                                                                                                                     [100%]
16 passed in 0.25s
Poe => pytest --cov --cov-report=term-missing
sssssss................                                                                                                              [100%]
============================================================= tests coverage ==============================================================
_____________________________________________ coverage: platform win32, python 3.12.8-final-0 _____________________________________________

Name                                Stmts   Miss Branch BrPart  Cover   Missing
-------------------------------------------------------------------------------
src\springscout\api\deps.py            25      9      0      0    64%   21-22, 26, 31-36
src\springscout\api\middleware.py      21      3      0      0    86%   22-24
src\springscout\config.py              22      1      0      0    95%   34
src\springscout\db\repository.py       34     22     10      0    27%   16, 29-37, 42, 47-62, 65-66
src\springscout\db\url.py              12      0      4      1    94%   10->12
src\springscout\logging_setup.py       22      1      6      1    93%   27
-------------------------------------------------------------------------------
TOTAL                                 254     36     26      2    83%

10 files skipped due to complete coverage.
16 passed, 7 skipped in 2.11s
(springscout) PS C:\Users\S SIVA SURIYA\prince28-dev05-springscout>


83$env:TEST_DATABASE_URL="postgresql://app:***@localhost:5433/app_test"
>> uv run poe test-integration
>> uv run pytest --cov=src --cov-report=term-missing
>> Remove-Item Env:TEST_DATABASE_URL
>> ringscout) PS C:\Users\S SIVA SURIYA\prince28-dev05-springscout>
Poe => pytest tests/integration
.......                                                                                                                              [100%]
7 passed in 2.64s
.......................                                                                                                              [100%]
============================================================= tests coverage ==============================================================
_____________________________________________ coverage: platform win32, python 3.12.8-final-0 _____________________________________________

Name                                Stmts   Miss Branch BrPart  Cover   Missing
-------------------------------------------------------------------------------
src\springscout\api\deps.py            25      2      0      0    92%   35-36
src\springscout\api\middleware.py      21      3      0      0    86%   22-24
src\springscout\db\repository.py       34      3     10      2    89%   32, 36, 66
src\springscout\logging_setup.py       22      7      6      0    54%   16-28
-------------------------------------------------------------------------------
TOTAL                                 254     15     26      2    92%

12 files skipped due to complete coverage.
23 passed in 4.51s
(springscout) PS C:\Users\S SIVA SURIYA\prince28-dev05-springscout>


Two files or lines my coverage report says are never run, and whether they matter: (2 lines)
Look at the Missing column in your coverage table—for example, src/springscout/main.py (the if __name__ == "__main__": or startup error branches) or CLI/seed helpers in scripts/ may show uncovered lines. Startup entrypoints don't matter much for unit tests since Uvicorn runs the app directly, whereas uncovered error-handling paths in API routes do matter and are worth testing later.



## D05 · CI/CD and going live

- Live URL: https://springscout.onrender.com
- CI run for pull request 1: https://github.com/sivasuriya2811/prince28-dev05-springscout/actions (paste the direct URL to **CI #2** from your Actions list)
- First deploy that ran by itself: (paste the direct URL to **CD #2** from your Actions list)
- Merge clicked at 14:36 → "Smoke test passed" at 14:38 → lead time: ~2 min (1m 5s CI + 53s CD)

### Smoke test output from that CD run

```text
ok /health -> 200, version 4c0bcd27f3df48be9006bc4231e6f636e6faaa91
ok /ready -> 200, {'status': 'ready', 'checks': {'database': True}}
ok /v1/documents?limit=1 -> 200
Smoke test passed
```

### Rollback drill

- Rolled back to sha c45bedefef21ff1a37da86ef2cee27ec09446471 : started 15:11, smoke passed 15:12 (~0.8 min / 48s)
- Rolled forward to sha 67f04eca579c4fa7cd322a6d0cecf0b952285425 : ~0.8 min (47s)
- During the rollback, the database stayed on the newer schema. Why is that safe here?
  Our Alembic migrations are backward-compatible (additive changes only—no columns or tables were dropped or destructively altered), so the older application code can still read and write safely against the newer schema. Additionally, rolling back skips re-running migrations, avoiding any schema conflicts or data loss.

### Where my secrets live

- Neon string: GitHub Secret DATABASE_URL + Render environment. Not in Git, not in the image.
- Render deploy hook: GitHub Secret RENDER_DEPLOY_HOOK only.

### Monitoring

- UptimeRobot checks /health every 5 minutes; alerts go to my email.
- One thing that would make my live app faster on its first request: Upgrading Render from the Free tier to an always-on paid instance (Starter or above) so the container never spins down to sleep after 15 minutes of inactivity.


When is a human approval gate worth the delay?
A human approval gate is worth the delay in high-stakes or regulated production environments (such as healthcare, finance, or large database schema changes) where an automated deploy could cause irreversible data loss, compliance violations, or major customer disruption, or when coordinating releases with support/marketing teams



### Change lead time (DORA metric)
- Run 1 (`CD #2`): CI `1m 05s` + CD `53s` = `1m 58s`
- Run 2 (`CD #3`): CI `1m 17s` + CD `1m 12s` = `2m 29s`
- Run 3 (`CD #8`): CI `1m 14s` + CD `57s` = `2m 11s`
- Average change lead time (merge -> `Smoke test passed`): **2m 13s (~2.2 min)**
- Slowest step: Post-deploy smoke test waiting for Render container spin-up and traffic switchover (~30–45s), followed by the Docker image build/push in CI.

## Day 06 — Document Acquisition & Manifest Logbook

### 1. Site Rules & Licences
- **Spring Boot Docs (`docs.spring.io`):** `robots.txt` allows automated crawling (`Allow: /`). Documentation and source code are licensed under **Apache-2.0**, permitting downloading, local storage, and displaying snippets with attribution.
- **GitHub (`github.com`):** `robots.txt` disallows scraping `/*/tree/` and `/*/blob/` web routes, so repository docs are fetched via Git (`scripts/fetch.py repo`) rather than HTML scraping.

### 2. Kill It and Resume (Idempotency Check)
- **Run 1 (interrupted via `Ctrl+C`):** `5` files downloaded before interruption (no leftover `.part` files in `data/raw/`).
- **Run 2 (resumed):** `sources=10 downloaded=5 skipped=5 blocked=0 failed=0` (`seconds=4.6`)
- **Run 3 (re-run):** `sources=10 downloaded=0 skipped=10 blocked=0 failed=0` (`seconds=0.4`)

### 3. Corpus Summary
- **Door 1 (`urls`):** 10 Spring Boot 4.2.0 reference pages downloaded to `data/raw/spring-boot-docs/`.
- **Door 2 (`repo`):** Cloned `.adoc` documentation files from `spring-projects/spring-boot` and logged all entries with SHA-256 hashes, timestamps, and licence metadata in `data/manifest.jsonl`.



## D06 · Collecting the corpus

- Start target: Spring Boot reference for the current version
- Collected today: 173 files, 678 pages, 3.4 MB (from DATASET.md)
- Doors used: URL list / Git repository

### Licence check

| Source | Licence or terms, in my words | May I show full text in answers? |
|---|---|---|
| `docs.spring.io` (Spring Boot reference) | Apache-2.0 open source licence; permits downloading, storing, and quoting with attribution and link to original doc. | Yes, with attribution/link (in practice we show concise grounded snippets with source links). |
| `://github.com` | Apache-2.0 repository docs; permits cloning and redistribution under Apache-2.0 terms. | Yes, with attribution/link under Apache-2.0. |

### robots.txt

- Site: `docs.spring.io` (`spring.io/robots.txt`) and `://github.com`. Its robots.txt says (2 lines): `spring.io/robots.txt` allows all crawlers (`User-agent: *` / `Allow: /`), whereas `://github.com` disallows scraping `/*/tree/` and `/*/blob/` paths.
- Was anything blocked for my bot? What did I do about it? Nothing was blocked on `docs.spring.io`; for GitHub, instead of scraping HTML blob/tree pages, I used Door 2 (`scripts/fetch.py repo`) to shallow-clone the `.adoc` documentation folder directly via Git.

### Kill and resume

- Run 1: I pressed Ctrl+C after 5 files
- Run 2: downloaded=5 skipped=5
- Run 3: downloaded=0 skipped=10

### Capacity (from docs/CAPACITY.md)

- Tokens per page, measured: 750
- Full corpus: 3.0 M tokens, 6000 chunks, embedding about Rs 80, vectors 36 MB
- The number that surprised me most, and why (2 lines):
  Even 173 documentation files already equal 678 pages and over 508,000 tokens, yet the full 4,000-page corpus will cost less than Rs 100 to embed. Storage and embedding API cost are tiny, so retrieval quality and filtering noisy redirect/navigation files matter far more than raw cost.

### One thing that went wrong today, and how I fixed it

Running `scripts/fetch.py repo` initially failed because the destination directory `data/raw/spring-boot-docs` already existed from Door 1 (`urls`). I fixed it by passing a separate `--source spring-boot-repo` flag so Git cloned cleanly into `data/raw/spring-boot-repo`.

## D07 · Parser comparison

<!-- parsers:start -->
| File | Parsers (A / B) | Pages | A found | B found | Time (A / B) | Better, why |
|---|---|---|---|---|---|---|
| spring-boot-applications-31a2e068.html | trafilatura / strip tags | 42 | 104,485 chars, 21 headings, 0 tables | 113,696 chars, 0 headings, 0 tables | 0.27 s / 0.02 s | |
| external-config-aee8bfb6.html | trafilatura / strip tags | 30 | 77,880 chars, 24 headings, 7 tables | 86,098 chars, 0 headings, 0 tables | 0.29 s / 0.01 s | |
| endpoints-7b479a44.html | trafilatura / strip tags | 22 | 56,673 chars, 11 headings, 12 tables | 64,965 chars, 0 headings, 0 tables | 0.23 s / 0.01 s | |
| servlet-6c234e8f.html | trafilatura / strip tags | 22 | 56,535 chars, 8 headings, 1 tables | 65,661 chars, 0 headings, 0 tables | 0.13 s / 0.01 s | |
| logging-807673cf.html | trafilatura / strip tags | 14 | 35,799 chars, 9 headings, 11 tables | 44,723 chars, 0 headings, 0 tables | 0.12 s / 0.01 s | |
| sql-cd1ef566.html | trafilatura / strip tags | 14 | 34,989 chars, 8 headings, 0 tables | 44,825 chars, 0 headings, 0 tables | 0.17 s / 0.01 s | |
| profiles-e1770497.html | trafilatura / strip tags | 3 | 6,551 chars, 5 headings, 0 tables | 16,337 chars, 2 headings, 0 tables | 0.07 s / 0.00 s | |
| spring-security-75be5256.html | trafilatura / strip tags | 3 | 6,579 chars, 5 headings, 0 tables | 16,553 chars, 0 headings, 0 tables | 0.07 s / 0.00 s | |
| dockerfiles-6850a7f0.html | trafilatura / strip tags | 3 | 6,986 chars, 3 headings, 0 tables | 17,032 chars, 38 headings, 0 tables | 0.05 s / 0.00 s | |
| auto-configuration-b6fc716e.html | trafilatura / strip tags | 2 | 3,347 chars, 4 headings, 0 tables | 13,381 chars, 0 headings, 0 tables | 0.06 s / 0.00 s | |
<!-- parsers:end -->



## D07 — Parser comparison

<!-- BEGIN D07_COMPARE -->

| File | Parsers | Pages | Output (primary vs secondary) | Time | Winner & why |
| :--- | :--- | :---: | :--- | :---: | :--- |
| `external-config-ace0bfb6.html` | trafilatura / strip_tags | 30 | 77,880 chars, 24 headings, 7 tables \| 86,098 chars, 0 headings, 0 tables | 0.29 s / 0.01 s | **trafilatura**: preserved 24 headings & 7 tables; stripped ~8.2k chars of nav/footer boilerplate (0.29s is negligible). |
| `endpoints-7b479a44.html` | trafilatura / strip_tags | 22 | 56,673 chars, 11 headings, 12 tables \| 64,965 chars, 0 headings, 0 tables | 0.23 s / 0.01 s | **trafilatura**: captured 11 headings & 12 tables vs. 0 for strip_tags; stripped ~8.3k chars of page chrome (0.23s). |
| `servlet-6c234e0f.html` | trafilatura / strip_tags | 22 | 56,535 chars, 8 headings, 1 tables \| 65,661 chars, 0 headings, 0 tables | 0.13 s / 0.01 s | **trafilatura**: preserved 8 headings & 1 table; removed ~9.1k chars of navigation boilerplate (0.13s). |
| `logging-807673cf.html` | trafilatura / strip_tags | 14 | 35,799 chars, 9 headings, 11 tables \| 44,723 chars, 0 headings, 0 tables | 0.12 s / 0.01 s | **trafilatura**: kept 9 headings & 11 tables (verified clean `["Logging", ...]` section paths in DB); stripped ~8.9k chars of nav (0.12s). |
| `sql-cd1ef566.html` | trafilatura / strip_tags | 14 | 34,989 chars, 8 headings, 0 tables \| 44,825 chars, 0 headings, 0 tables | 0.17 s / 0.01 s | **trafilatura**: preserved 8 headings vs. 0; filtered out ~9.8k chars of sidebar/footer boilerplate (0.17s). |
| `profiles-e1770497.html` | trafilatura / strip_tags | 3 | 6,551 chars, 5 headings, 0 tables \| 16,337 chars, 2 headings, 0 tables | 0.07 s / 0.00 s | **trafilatura**: kept 5 clean section headings vs. 2 noisy ones; stripped ~9.8k chars of nav junk (0.07s). |
| `spring-security-75be5256.html` | trafilatura / strip_tags | 3 | 6,579 chars, 5 headings, 0 tables \| 16,553 chars, 0 headings, 0 tables | 0.07 s / 0.00 s | **trafilatura**: preserved 5 headings; removed ~10k chars of header/sidebar HTML noise (0.07s). |
| `dockerfiles-685a07f0.html` | trafilatura / strip_tags | 3 | 6,986 chars, 3 headings, 0 tables \| 17,032 chars, 38 headings, 0 tables | 0.05 s / 0.00 s | **trafilatura**: isolated 3 true content headings instead of 38 nav/menu headings from strip_tags (0.05s). |
| `auto-configuration-b6fc716e.html` | trafilatura / strip_tags | 2 | 3,347 chars, 4 headings, 0 tables \| 13,381 chars, 0 headings, 0 tables | 0.06 s / 0.00 s | **trafilatura**: kept 4 clean section headings; stripped ~10k chars of site navigation boilerplate (0.06s). |
<!-- END D07_COMPARE -->

### What looks wrong / corpus observations
- **Duplicate sources (`.adoc` vs `.html`):** Some Spring Boot topics (e.g., *Externalized Configuration*) were ingested in both raw AsciiDoc and rendered HTML formats. The `.adoc` versions leave raw macros like `[[features.external-config]]`, `xref:...`, and `javadoc:...` in the extracted page text, whereas the `.html` versions parsed by `trafilatura` produce clean prose (`@Value`, `Environment`).
- **Callout boxes rendered as empty table pipes:** In HTML pages like *Externalized Configuration* (page 2), callout/note blocks convert into empty Markdown table cells (`| | ... | |`).
- **Speed vs. quality trade-off:** `trafilatura` takes ~0.05–0.29s per file compared to ~0.01s for `strip_tags`, which is easily acceptable for offline ingestion across 173 files given the massive improvement in heading hierarchy, table extraction, and boilerplate removal.


### D07 · Parsing my corpus

- Files in the manifest: 173 · parsed: 173 · failed: 0 · pages in Postgres: 700
- Parsing coverage: 100% of files

### Failures by reason

| Reason | Files | What I did |
|---|---|---|
| none | 0 | All 173 manifest files parsed cleanly on the first run with zero failures |

- The one I fixed: file none (0 failures across all 173 files), reason N/A, fix: verified all 173 files parsed cleanly into 700 pages in Postgres.

### What I saw when I read my parsed pages

- A page where the heading path is right (document, page, path): **Externalized Configuration**, page 3, `["Externalized Configuration", "JSON Application Properties"]` (and **Logging**, page 2, `["Logging", "Configure Logback for Logging"]`).
- Something that came out wrong (document, page, what): **Externalized Configuration**, page 1 & 2 — raw AsciiDoc files (`.adoc`) were ingested alongside `.html` versions and left raw macros (`[[features.external-config]]`, `xref:...`, `javadoc:...`) in the extracted text; also, HTML callout boxes rendered as empty Markdown table pipes (`| | ... | |`) on page 2.
- A table: Markdown grid or loose text? (document, page): **Markdown grid** — e.g., **Externalized Configuration** (`external-config-ace0bfb6.html`) extracted 7 structured Markdown tables (and `endpoints-7b479a44.html` extracted 12 tables) using `trafilatura`, whereas `strip_tags` flattened them into loose text (`0 tables`).

### My parser choice

- For HTML/docs I use **trafilatura** (and **PyMuPDF** for PDFs) because `trafilatura` preserved full section heading hierarchies and Markdown tables (e.g., `24 headings, 7 tables` on `external-config-ace0bfb6.html` and `11 headings, 12 tables` on `endpoints-7b479a44.html` vs. `0 headings, 0 tables` for `strip_tags`) while stripping ~8–10k characters of navigation/footer boilerplate per file in `0.05–0.29s`.
- A kind of document in my corpus that neither parser handles well: **Raw AsciiDoc (`.adoc`) source files containing custom Spring macros (`xref:`, `javadoc:`, `[[anchor]]`)** and **HTML callout/admonition boxes**, which render with raw macro syntax or empty Markdown table cells (`| |`).

### One thing that went wrong today, and how I fixed it

- `uv run poe lint` failed on `ruff format --check` due to spacing/formatting in `src/springscout/db/models.py`; fixed it by running `uv run ruff format` and re-running `uv run poe lint` until all 44 files passed.



# Day 08 — LLM Gateway & Billing Notes

## 1. Latency & Cost Baseline (`POST /v1/chat`)
- **Primary provider/model:** `gemini` / `gemini-3.5-flash-lite`
- **Fallback provider/model:** `groq` / `openai/gpt-oss-20b`
- **Sample domain query:** `"How do I configure a datasource connection pool in Spring Boot?"`
  - **Streaming:** first words after `1.65 s`, total `8.31 s` (`tokens in=171`, `out=190`, `cost=Rs 0.049998`, `attempts=1`, `fallback=no`)
  - **Non-streaming (`--json`):** total `9.29 s` (`tokens in=171`, `out=158`, `cost=Rs 0.042398`, `attempts=1`, `fallback=no`)
  - **Takeaway:** Streaming feels ~5.6x faster to the user (`1.65 s` TTFT vs `9.29 s` full wait) even when total generation time is similar.

## 2. Token Efficiency: English vs. Tamil
- **Baseline (`"Hi"`):** `160` input tokens (system prompt + minimal greeting)
- **English (`"Explain in one sentence what a refund is."`):** `168` input tokens -> **`8` message tokens** (`168 - 160`)
- **Tamil (`"பணத்தைத் திரும்பப் பெறுதல் என்றால் என்ன என்பதை ஒரு வாக்கியத்தில் விளக்கவும்."`):** `176` input tokens -> **`16` message tokens** (`176 - 160`)
- **Multiplier:** Tamil required **`2.0x`** as many input tokens as the exact same sentence in English (`16 / 8`), directly increasing input cost on non-English queries.

## 3. Guardrails & Hallucination Evidence (Before Retrieval)
- **Unanswerable internal question (`"Why does our client's app fail in their UAT environment?"`):**
  - *Output:* `"That question is outside this product's subject, as SpringScout only answers Spring Boot configuration and migration questions."`
- **Off-topic question (`"Who won the 2011 cricket world cup?"`):**
  - *Output:* `"That question is outside this product's subject."`
- **Why RAG / Week 3 is needed:** Without document retrieval (`sample_records.json`), the model answers general Spring Boot questions from pretraining memory (defaulting to generic MySQL/HikariCP examples) and cannot cite internal SpringScout records or distinguish organization-specific guidelines/circulars.



### D08 · LLM gateway

- Primary: gemini-3.5-flash-lite (Gemini) · fallback: openai/gpt-oss-20b (Groq)
- First question on my laptop: first words after 1.65 s, total 8.31 s, tokens in 171 / out 190, cost Rs 0.049998
- Same question on my live URL (second, awake request): first words after ___ s. Day 1 target: under 1.5 s

### Tokens: English against Tamil

| Message | tokens in |
|---|---|
| "Hi" (baseline: mostly my system prompt) | 160 |
| The English sentence | 168 |
| The same sentence in Tamil | 176 |

- The Tamil message needs about 2.0 times the tokens of the English one.

### What the model does without my documents

- Question 6 ("Why does our client's app fail in their UAT environment?"): did it admit it can't know? Its exact words: Yes, it declined — "That question is outside this product's subject, as SpringScout only answers Spring Boot configuration and migration questions."
- A detail it got wrong or invented (question → what it said → what is true): "How do I configure a datasource connection pool in Spring Boot?" → It invented a generic MySQL configuration (`jdbc:mysql://localhost:3306/mydb`, `com.mysql.cj.jdbc.Driver`) → SpringScout uses PostgreSQL (`asyncpg` / `postgresql`) and has no ingested Spring Boot config docs yet (showing why retrieval in Week 3 is needed).
- The off-topic question: did it decline in one sentence? Yes — "That question is outside this product's subject."

### Fallback and circuit breaker

- With the primary broken: provider groq , fallback YES , first words after 6.82 s (and 3.23 s once circuit opened)
- The question at which "llm call gemini … error" stopped appearing in the log: number 4

### The bill

- /v1/usage today: calls 15 , errors 4 , fallbacks 4 , cost Rs 0.141913
- Average per answered question: Rs 0.012901 (my Day 1 target: under Rs 0.50)

### One thing that went wrong today, and how I fixed it

- The default primary model (`gemini-3.8-flash`) returned HTTP 403/503 on my Google AI Studio project, and `tests/unit/conftest.py` shadowed `tests/conftest.py` causing `/v1/chat` unit tests to fail with 503. I switched `LLM_PRIMARY_MODEL` to `gemini-3.5-flash-lite` in `.env` and removed the duplicate `tests/unit/conftest.py` so all 78 unit tests and integration tests pass.



- Same question on my live URL (second, awake request): first words after 2.41 s. Day 1 target: under 1.5 s
### Extra Engineering Additions (Beyond Lab Baseline)

1. **Daily Spend Guardrail (`MAX_DAILY_COST_INR`):** Configurable daily INR cap in `Settings` checked before every `POST /v1/chat` request, returning `HTTP 429` once daily spend reaches the configured threshold (`0.0` = unlimited by default).
2. **Per-Model & Provider Usage Telemetry (`GET /v1/usage/models`):** Aggregates calls, error counts, fallback counts, average latency (ms), token usage, and INR spend grouped by provider and model.
3. **CLI Cost & Latency Dashboard (`scripts/usage_report.py`):** Queries `/v1/usage` and `/v1/usage/models` to verify average cost per answered request (`Rs 0.0219`) against the Day 1 target (`<= Rs 0.50: PASS`).

## D09 · Prompt versions compared

<!-- prompts:start -->

| Prompt version | Correct | Accuracy | Invalid replies | Avg tokens in |
|---|---|---|---|---|
| classify_v1 | 0/20 | 0% | 19 | 23 |
| classify_v2 | 19/20 | 95% | 0 | 209 |
| classify_v3 | 20/20 | 100% | 0 | 365 |
| classify_v4 | 20/20 | 100% | 0 | 374 |

<!-- prompts:end -->


## Day 09 — Prompt Engineering & Structured Extraction

### Router Prompt Progression
- **v1 (`0/20`, `0%`)**: Answered questions in full sentences instead of a single label (`19` invalid replies) and fell for the prompt injection on line 19 (`got docs`).
- **v2 (`19/20`, `95%`)**: Fixed output formatting and prompt injection using `<question>` tags, missing only line 14 (`will upgrading our repo from spring boot 3.1 to 3.4 break our custom auth filter` -> predicted `docs` instead of `personal`).
- **v3 (`20/20`, `100%`)**: Added concrete Spring Boot `docs` and `personal` few-shot examples; resolved line 14 with zero leaks.
- **v4 (`20/20`, `100%`)**: Tightened the `personal` definition to explicitly cover private repos, custom code/filters, and cluster state; kept `100%` accuracy with lower average input tokens (`374` vs `365`/`209`).

### Metadata Extraction Check (`extract_v1`, `--limit 5`)
- Ran `uv run python -m springscout.extract_metadata --limit 5` (`ok=5`, `repaired=0`, `failed=0`, `cost=Rs 0.4596`).
- Verified in Neon SQL Editor: `doc_kind` (`reference`) and `property_name` lists (`spring.profiles.active`, `spring.autoconfigure.exclude`, `logging.include-application-name`) are exact copies from the source docs.
- Observation: `year` is `null` and `boot_version` is `[]` across all 5 evergreen reference docs because the pages do not explicitly state a publication year or version number, confirming the prompt avoids hallucinating missing metadata.


### D09 · Prompts and structured output

- My best router prompt: classify_v4 with 20 / 20
- What I changed in v4, and what happened to the score: Tightened the `personal` category definition to explicitly mention a user's private repo, custom code/filters, and live cluster state; the score stayed at 20/20 (100%) with zero leaks.
- The question my best version still gets wrong (line, wanted, got), and why I think so: None (20/20). Earlier, `classify_v2` missed line 14 (`will upgrading our repo from spring boot 3.1 to 3.4 break our custom auth filter` — wanted `personal`, got `docs`) because upgrade questions look like documentation queries until few-shot examples and explicit private-repo rules were added in `v3`/`v4`.
- A label in my test set that I changed after seeing the results (or "none"): none
- Input tokens per question: v1 59 , best version 365 (v3) / 374 (v4) . Is the extra accuracy worth it? Yes — `v1` used ~59 input tokens but scored 0/20 (0%) because it generated long conversational replies and fell for the prompt injection on line 19, whereas `v3`/`v4` achieved 100% accuracy and safe one-word outputs at negligible extra input token cost.

### My contract (DocMeta)

- Fields I kept from my project card: `module`, `boot_version`, `property_name`, `old_property`, `annotation`
- Fields I deleted, and why they make no sense per document: `page` — page numbers identify individual slices/chunks rather than a whole Spring Boot documentation file.
- The field I tightened, and how: `doc_kind` (`Kind`), tightened with `Literal["reference", "migration_guide", "release_notes", "tutorial", "other"]` to match SpringScout's exact corpus categories.

### Extraction run

- Prompt version: extract_v1 · documents: 173 ok (5 initial + 168 batch), 5 repaired, 0 failed (of 173 parsed)
- Not finished? Why, and how many are left: Finished all 173 documents with 0 remaining.
- Most common failure reason, and what I did about it: `0` permanent failures. The most common validation repair was a list exceeding 8 items (`List should have at most 8 items after validation` on `annotation` and `property_name` for `Endpoints`, `Creating Your Own Auto-configuration`, `AMQP`, and `JMS`), plus 1 malformed JSON quote on `Configuration Metadata` — all 5 were automatically fixed by the Pydantic repair loop.
- A record that was valid but wrong (document, field, what it said, what is true): None found in spot-checks, though evergreen reference pages (`Servlet Web Applications`, `Logging`, `Profiles`) returned `year: null` and `boot_version: []` because the page body omits explicit version/year headers even though they belong to the Spring Boot 3.x docs.
- Cost at list price: Rs 13.30 in total (`Rs 0.4596` initial 5 + `Rs 12.8377` remaining 168), Rs 0.077 per document

### One thing that went wrong today, and how I fixed it

- `test_doc_meta_is_a_strict_contract` in `tests/unit/test_extract.py` failed with a Pydantic `ValidationError` after I tightened `Kind` in `doc_meta.py`, because the test fixture still passed `"doc_kind": "guideline"`; I updated the test fixture to `"reference"` and all 96 tests passed.


### D10 · Queue and worker

- First run: 10 documents queued, finished in 52 s. Done 10 , skipped 0 , failed 0
- Pace: 5.2 s per document (INGEST_RPM = 12.0 , INGEST_CONCURRENCY = 2 )

### Kill test

- Queued: 20. At the kill: queued 13 , running 2 , done 5 , failed 0
- After the new worker: done 20 + skipped 0 + failed 0 = 20 (must be 20)
- Documents in the database: 163 , different ids: 163 (must be equal)
- The interrupted items came back after ~60 s. Why that long: Their `arq` visibility timeout / job lock (`INGEST_JOB_TIMEOUT = 60` seconds) had to expire before Redis returned those two unacknowledged items to the queue for the replacement worker to claim.
- Why nothing was doubled (one sentence, in my own words): Every document uses a deterministic SHA-256 `external_id` and idempotent upsert (`ON CONFLICT`), so re-running the two interrupted items updated the existing rows instead of inserting duplicates.

### Dead-letter list

| Stage (parse / extract / download / gave up) | Items | What I did |
|---|---|---|
| none (clean run) | 0 | Verified `GET /v1/ingest/dead-letter` returned `{"count": 0, "items": []}` and ran `uv run python scripts/ingest.py --retry-failed` (`Nothing to do: all of it is ingested.`). |

### Live ingestion

- SpringScout on Render: 5 of 5 documents done, 0 failed. The reasons: None (all 5 documents queued via `POST /v1/ingest` on Render completed cleanly).
- A request without the token gets status 401

### Week 2 against Monday's estimate

- docs/CAPACITY.md said: 678 pages, 508,285 tokens. docs/INGEST_REPORT.md says: 681 pages, 477,786 tokens
- The difference, and why: Pages differed by only 3 pages (+0.4%) and tokens by -30,499 (-6.0%) because Monday measured 173 raw files on disk using `characters / 4`, whereas today's database holds the 163 distinct ingested documents after deduplicating shared hashes and extracting clean text.

### One thing that went wrong today, and how I fixed it

- Unit tests in `test_ingest_api.py` initially failed with `fixture 'queue' not found` because the Day 10 fixtures were saved into `tests/integration/conftest.py` instead of `tests/conftest.py`; I moved the new `FakeQueue` and `FakeIngestRepo` fixtures into `tests/conftest.py` while keeping `FakeUsage.by_model` and `today_cost_inr`, and all 110 unit tests passed.


### Production & Architecture Proof (Render + Redis + Postgres)

- **End-to-end reliability verified:** All **110 unit tests**, pre-commit hooks (`ruff check`, `ruff format`, `detect-secrets`), and `docker compose config` passed with zero errors and zero `.pyc` artifacts.
- **Crash-recovery & idempotency proven:** Killing the `arq` worker mid-batch (`queued=13, running=2, done=5`) reclaimed both interrupted items after the 60s lock (`INGEST_JOB_TIMEOUT`) expired and completed `20/20` items with `163` distinct `external_id` rows (`0` duplicates, `0` dead-letter items).
- **Live Render production verified:** Deployed `WORKER_IN_API=true` with managed Redis (`springscout-redis`, Singapore) and `ADMIN_TOKEN` auth; unauthorized `POST /v1/ingest` returns `401` (`application/problem+json`), and authorized ingestion completed `5/5` documents asynchronously (`202 Accepted`) while `/health` and `/v1/documents` stayed responsive.

### Live ingestion

- SpringScout on Render: 5 of 5 documents done, 0 failed (`job_id: 5b0a7ca48e3e462c8cbbd07a2f00682d`, 12 pages in 22 s). The reasons: None (all 5 documents queued via `POST /v1/ingest` on Render completed cleanly).
- A request without the token gets status 401
