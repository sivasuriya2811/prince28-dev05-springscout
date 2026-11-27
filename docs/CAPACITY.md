# Capacity plan: SpringScout

Full corpus target: + 2.7 reference, migration guide, release notes 3.0-3.5, Framework reference (4,000+ pages)

<!-- generated:start -->
## Measured on my start corpus (2026-11-23 10:04 UTC)

| What | Value |
|---|---|
| Files | 173 |
| Size on disk | 3.4 MB |
| Pages (PDF pages + 1 per 3,000 characters of text/HTML) | 678 |
| Characters of text | 2,033,140 |
| Estimated tokens (characters / 4) | 508,285 |
| Tokens per page | 750 |
| PDFs with almost no text (scanned? OCR is Day 7) | 0 |
| Files not measured (zip, xlsx, unreadable) | 0 |

## Estimate for the full corpus (target: 4,000 pages)

| What | How | Value |
|---|---|---|
| Scale factor | target / measured | x 5.9 |
| Tokens | measured tokens x scale | 3.00 M |
| Raw files | measured MB x scale | 20 MB |
| Chunks | tokens / 400 x 1.15 overlap | 8,625 |
| Embedding cost, one time | tokens x 1.15 x $0.15 per 1M | $0.52 = Rs 49 |
| Vector storage | chunks x 768 numbers x 4 bytes | 26 MB |
| Text in Postgres | characters x scale x 1.2 | 14 MB |

Assumptions: 4 characters per token, 400-token chunks, 768-dimension embeddings at $0.15 per 1M tokens, Rs 95 per US dollar.
<!-- generated:end -->

## What I conclude

- **Storage and embedding budget at 4,000 pages:** Scaling our 3.4 MB (678-page) start corpus by 5.9× produces ~20 MB of raw files, ~3.00M tokens (8,625 chunks), 26 MB of vector storage, and 14 MB of Postgres text, with a one-time embedding cost of $0.52 (Rs 49)—well within free-tier database and API budgets.
- **Least certain estimate and how to measure it:** Estimated tokens (508,285) is the roughest number because `characters / 4` approximates prose rather than dense AsciiDoc tables and Java/YAML configuration snippets; we validate it directly against real token usage tracked in `llm_calls` during ingestion.
- **What changes if the corpus grows 10× (40,000 pages):** Raw files reach ~200 MB, vector storage grows to ~260 MB, and embedding time/cost scales 10× (~Rs 490), requiring an async background worker queue (`arq` + Redis), rate-limited batching, incremental SHA-256 manifest ingestion, and `pgvector` HNSW indexing.
