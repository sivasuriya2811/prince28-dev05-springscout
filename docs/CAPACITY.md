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

• Question 1 & 2 (check your exact wording at the bottom of docs/CAPACITY.md—typically about storage/embedding cost and latency at 4,000 pages): Scale your 3.4 MB (678 pages) up by ~5.9× (4,000 / 678), giving ~20 MB on disk and ~3.0M tokens.
• Question 3 ("Which number above am I least sure about, and how will I measure it better?"): The estimated tokens (508,285) because characters / 4 is a rough heuristic for AsciiDoc/code blocks; I will measure it accurately using the actual model tokenizer (tiktoken) during Day 07/08 chunking.
• Question 4 ("What changes if the corpus grows 10 times?"): Disk size grows to ~34 MB (or ~200 MB at 40,000 pages) and embedding time/API cost scales 10×, requiring batching, incremental manifest-based indexing, and pgvector HNSW/IVFFlat indexing instead of full re-ingestion.
