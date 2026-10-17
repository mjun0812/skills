# DuckDBのdocsを検索する

DuckDB公式が配布している全文検索のindexを手元にcacheし、BM25で検索する。関数名やオプションを推測で書き直す前に使う。

## indexを用意する

cacheは `~/.duckdb/docs/` に置き、2日より古ければ取り直す。

```bash
mkdir -p "$HOME/.duckdb/docs"
F="$HOME/.duckdb/docs/duckdb-docs.duckdb"
if [ ! -f "$F" ] || [ $(( ($(date +%s) - $(stat -f %m "$F" 2>/dev/null || stat -c %Y "$F")) / 86400 )) -gt 2 ]; then
    duckdb -c "
INSTALL httpfs; INSTALL fts; LOAD httpfs;
ATTACH 'https://duckdb.org/data/docs-search.duckdb' AS remote (READ_ONLY);
ATTACH '$F.tmp' AS tmp;
COPY FROM DATABASE remote TO tmp;
" && mv "$F.tmp" "$F"
fi
```

## 検索する

検索語は、質問文から関数名・SQLのキーワード・名詞だけを抜き出して作る (例: 「CSVを列名で揃えて読みたい」なら `union_by_name read_csv`)。

```bash
duckdb "$HOME/.duckdb/docs/duckdb-docs.duckdb" -readonly -json -c "
LOAD fts;
SELECT page_title, section, url, text,
       fts_main_docs_chunks.match_bm25(chunk_id, 'union_by_name read_csv') AS score
FROM docs_chunks
WHERE score IS NOT NULL AND version = 'lts'
ORDER BY score DESC
LIMIT 5;
"
```

`version` は `lts`・`current`・`blog` がある。手元のduckdbより新しい機能を調べるときは `current` にするか、条件を外す。

結果が無ければ、検索語を1〜2語に減らして検索し直す。それでも無ければ https://duckdb.org/docs を直接参照する。
