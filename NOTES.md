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
