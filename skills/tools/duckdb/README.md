# duckdb

[日本語](README_ja.md)

Use the DuckDB CLI to check the schema of record-based data files before aggregating, inspecting, converting or joining them. Supported data includes JSONL / CSV / TSV / Parquet, JSON arrays of records, and agent session logs.

Use it to check row counts and distributions in data files. Also use it to check their keys and types, or to find duplicates and missing values. It is also for aggregating across many files and converting formats. Reach for it whenever you are about to write a Python or awk script for these tasks. It also works on files in S3, GCS, or over HTTPS. Do not use it just to pull a value out of a single JSON document (jq is enough) or to edit files.

## Usage

- "Check what keys this JSONL has and whether it has duplicates or type drift"
- "Compute the error rate per tool from the session logs"
- "Average these experiment result CSVs per model"
- "Convert this CSV to Parquet"

## Behavior

- Checks the schema with `DESCRIBE` / `SUMMARIZE` before aggregating, and writes SQL with the column names and types it confirmed. For columns with mixed types, it looks at the breakdown with `json_type()`.
- Prints output as `-csv` or `-markdown`, and returns only the rows it needs through aggregation or `LIMIT`.
- Reads CSVs with differing columns with `union_by_name`, and JSONL whose records differ in shape with `from_json` and `unnest`.
- Knows how to avoid the SQL errors that actually came up most often (aliases without `AS`, `->>` mixed with `AND`, missing statement separators).
- When unsure about a function name or syntax, caches DuckDB's official full-text search index locally and searches it ([references/docs-search.md](references/docs-search.md)).
- Reads files in S3, R2, GCS, or over HTTPS without downloading them ([references/remote.md](references/remote.md)).

## Dependencies

- `duckdb` CLI
- DuckDB's `httpfs` and `fts` extensions for docs search and remote files (installed automatically on first use)

## Source

This skill combines five skills from [duckdb/duckdb-skills](https://github.com/duckdb/duckdb-skills) (MIT License) into one. They are `read-file` / `query` / `convert-file` / `duckdb-docs` / `s3-explore`. It is rewritten for agents to use in the middle of a task. The docs search procedure and the way to read remote files are based on `duckdb-docs` and `s3-explore`, respectively.

See [SKILL.md](SKILL.md) for the full procedure.
