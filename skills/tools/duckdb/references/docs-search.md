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
ATTACH '$F.tmp' AS tmp (STORAGE_VERSION 'v1.5.0');
COPY FROM DATABASE remote TO tmp;
" && mv "$F.tmp" "$F"
fi
```

公式のindexはduckdb 2.0以降でしか開けない。`STORAGE_VERSION 'v1.5.0'` で書き出したcacheは、1.5でも2.0でも読める。
duckdb 1.5で実行すると `ATTACH` が `IO Error` になるが、既存のcacheが残っていればそのまま検索に使える。

## 検索する

検索語は、質問文から関数名・SQLのキーワード・名詞だけを抜き出して作る (例: 「CSVを列名で揃えて読みたい」なら `union_by_name read_csv`)。

```bash
duckdb "$HOME/.duckdb/docs/duckdb-docs.duckdb" -readonly -json -c "
INSTALL fts; LOAD fts;
SELECT page_title, section, url, text, score
FROM (
  SELECT *, fts_main_docs_chunks.match_bm25(chunk_id, 'union_by_name read_csv') AS score
  FROM docs_chunks
  WHERE version <> 'blog'
)
WHERE score IS NOT NULL
ORDER BY score DESC
LIMIT 5;
"
```

`score` は副問合せの中で求める。duckdb 2.0では、`match_bm25` の別名を同じ `SELECT` の `WHERE` で参照するとBinder Errorになる。

`version` 列は、`2.0` のような最新版のdocsのversionと、blog記事を表す `blog` に分かれる。blog記事も探すときは `WHERE version <> 'blog'` を外す。
indexは最新版のdocsだけを含む。手元のduckdbが古いときは、見つけた関数が手元にあるかを `SELECT DISTINCT function_name FROM duckdb_functions() WHERE function_name = '<関数名>'` で確かめる。

結果が無ければ、検索語を1〜2語に減らして検索し直す。それでも無ければ https://duckdb.org/docs を直接参照する。
