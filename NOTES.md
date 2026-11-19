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
