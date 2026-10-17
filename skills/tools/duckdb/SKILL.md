---
name: duckdb
description: >-
  DuckDB CLIで、レコードの集まりからなるデータファイル (JSONL・CSV・TSV・Parquet・レコード配列のJSON、agentのsessionログなど) を、
  schemaを確かめてから集計・検査・変換・突き合わせするSkill。
  データファイルの件数・分布・キーや型・重複や欠損を調べるとき、複数ファイルを横断して集計するとき、形式を変換するとき、
  またはそのためにPythonやawkのscriptを書こうとしたときに使うこと。S3・GCS・HTTPS上のファイルにも使う。
  単一のJSONから値を取り出すだけの場合 (jqで足りる) や、ファイルの編集には使わない。
---

# duckdb

データを推測で扱わず、schemaを確かめてから集計するためのskill。
Pythonでレコードを処理すると、先頭の1行からキーを推測して書き始めがちで、型の揺れや欠損に気づかない。
duckdbは全行を読んでschemaを推論し、`DESCRIBE` / `SUMMARIZE` で型・件数・欠損の割合をまとめて返す。そのうえでSQLを書けば、答えは正確になる。

## 進め方

1. **schemaを確かめる。** 集計の前に、読み込み方を決めて `DESCRIBE` する。値の範囲と欠損まで見たいときは `SUMMARIZE` を使う。
2. **確かめた列名と型でSQLを書く。** 型が `JSON` になった列は、値の型が揃っていない。集計の前に `json_type()` で内訳を見る。
3. **必要な行だけを出す。** 出力は `-csv` か `-markdown` にし、`LIMIT` や集計で行数を絞る。既定の罫線付きの表は、横に長くなりcontextを圧迫する。

```bash
duckdb -csv -c "
DESCRIBE FROM read_json('logs/*/*.jsonl');
SELECT json_type(meta.difficulty) AS t, count(*) AS n FROM read_json('data/eval_set.jsonl') GROUP BY ALL;
"
```

## 読み込み方

| データ                                        | 読み方                                                                                                                              |
| --------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------- |
| CSV・TSV                                      | `read_csv('results/*.csv', union_by_name = true)`。ファイルごとに列が違ってもよい                                                   |
| JSONL・JSON配列                               | `read_json('data/*.jsonl')`。ネストはSTRUCTとLISTになり、`meta.source` のように参照できる                                           |
| Parquet                                       | `read_parquet('*.parquet')`、またはファイル名をそのまま `FROM 'x.parquet'`                                                          |
| レコードごとに形が違うJSONL (sessionログなど) | `read_json(..., filename = true)` で読み、形の揃わない列 (`JSON` 型) は `from_json(col, '["json"]')` を `unnest` して要素ごとに扱う |
| どの列がどこから来たか必要なとき              | `filename = true` を付けて、`regexp_extract(filename, ...)` でプロジェクト名などを取り出す                                          |

形の違う配列を要素に分解する例を示す。

```sql
WITH items AS (
  SELECT regexp_extract(filename, 'logs/([^/]+)/', 1) AS project,
         unnest(from_json(message.content, '["json"]')) AS c
  FROM read_json('logs/*/*.jsonl', filename = true)
  WHERE json_type(message.content) = 'ARRAY'
)
SELECT project, json_extract_string(c, '$.name') AS tool, count(*) AS n
FROM items
WHERE json_extract_string(c, '$.type') = 'tool_use'
GROUP BY ALL ORDER BY ALL;
```

## SQLでつまずく点

実際のエラーの大半は次の3つだった。

- **別名には必ず `AS` を付ける。** `c->>'name' name` は `name` がキーワードなので構文エラーになる。`type`・`key`・`value`・`first`・`last`・`session` なども同じ。
- **`->>` を `AND` / `OR` の条件に括弧なしで書かない。** `j->>'a' = 'x' AND j->>'b' = 'y'` は型変換エラー (`Failed to cast value to numerical`) になる。`(j->>'a') = 'x'` と括弧で囲むか、`json_extract_string(j, '$.a')` を使う。
- **複数の文は `;` で区切る。** `-c` に渡したSQLで区切りを忘れると、次の `SELECT` で構文エラーになる。

関数名や構文に自信がないときは、推測で書き直す前に [references/docs-search.md](references/docs-search.md) の手順で公式docsを引く。

## 変換と書き出し

```sql
COPY (FROM read_csv('in.csv')) TO 'out.parquet';           -- 拡張子で形式が決まる
COPY (FROM 'in.parquet') TO 'out.jsonl' (FORMAT json);
```

入力ファイルを上書きしない。書き出し先は別のパスにする。

## リモートのファイル

S3・R2・GCS・HTTPS上のファイルは、ダウンロードせずに読める。認証と一覧の取り方は [references/remote.md](references/remote.md) を参照する。
