---
name: duckdb
description: >-
  DuckDB CLIでデータファイルの調査、抽出、集計、結合、形式変換とDuckDBの仕様確認を行うSkill。
  レコードの集まりからなるデータファイル (JSONL・CSV・TSV・Parquet・レコード配列のJSON、agentのsessionログなど) は、schemaを確かめてから扱う。
  データファイルの件数・分布・キーや型・重複や欠損を調べるとき、複数ファイルを横断して集計するとき、形式を変換するとき、
  またはそのためにPythonやawkのscriptを書こうとしたときに使うこと。S3・GCS・HTTPS上のファイルにも使う。
  単一のJSONから値を取り出すだけの場合 (jqで足りる) や、ファイルの編集には使わない。
---

# duckdb

DuckDB CLIでデータファイルの調査、抽出、集計、結合、形式変換と、DuckDBの仕様の確認に使うSkill。
duckdbは全行を読んでschemaを推論するため、型の揺れや欠損を集計の前に把握できる。

## 進め方

1. **schemaを確かめる。** レコードの集まりからなるデータファイル (JSONL・CSV・TSV・Parquet・レコード配列のJSON、agentのsessionログなど) は、集計の前に読み込み方を決めて `DESCRIBE` する。値の範囲と欠損まで見たいときは `SUMMARIZE` を使う。
2. **DuckDB固有の関数やオプションは、書く前に調べる。** 標準SQL (`SELECT`・`WHERE`・`GROUP BY`・`JOIN`・集約関数) の外にあるもの (`read_*` や `COPY` のオプション、JSON・LIST・STRUCTの関数、拡張など) を使うときは、[references/docs-search.md](references/docs-search.md) の手順で引数と返り値を確かめてから書く。エラーが出たときも、推測で直さずにdocsを引く。
3. **確かめた列名と型でSQLを書く。** 型が `JSON` になった列は、値の型が揃っていない。集計の前に `json_type()` で内訳を見る。
4. **必要な行だけを出す。** 出力は `-csv` か `-markdown` にし、`LIMIT` や集計で行数を絞る。既定の罫線付きの表は、横に長くなりcontextを圧迫する。

```bash
duckdb -csv -c "
DESCRIBE FROM read_json('data/*.jsonl');
SELECT json_type(col) AS t, count(*) AS n FROM read_json('data/*.jsonl') GROUP BY ALL;
"
```

## 読み込み方

| データ                                          | 読み方                                                                                        |
| ----------------------------------------------- | --------------------------------------------------------------------------------------------- |
| CSV・TSV                                        | `read_csv('results/*.csv', union_by_name = true)`。ファイルごとに列が違ってもよい             |
| JSONL・JSON配列                                 | `read_json('data/*.jsonl')`。ネストはSTRUCTとLISTになり、`meta.source` のように参照できる     |
| Parquet                                         | `read_parquet('*.parquet')`、またはファイル名をそのまま `FROM 'x.parquet'`                    |
| Excel・SQLite・地理データなど、拡張が必要な形式 | [references/formats.md](references/formats.md) の表で、拡張・読み方・書き出しの指定を確かめる |
| レコードごとに形が違う列                        | `JSON` 型になる。配列は `from_json(col, '["json"]')` を `unnest` して要素ごとに扱う           |
| 複数のファイルを横断するとき                    | `filename = true` を付けて、各行がどのファイルから来たかを残す                                |

次の例は、配列と配列以外の値が混在する列 `col` から、配列の行だけを選んで要素ごとの行に分け、要素の `kind` ごとに件数を数える。

```sql
SELECT json_extract_string(e, '$.kind') AS kind, count(*) AS n
FROM (
  SELECT unnest(from_json(col, '["json"]')) AS e
  FROM read_json('data/*.jsonl')
  WHERE json_type(col) = 'ARRAY'
)
GROUP BY ALL;
```

## SQLを書くときの注意

- **別名には必ず `AS` を付ける。** 別名がキーワードと重なると、`AS` なしでは構文エラーになる。
- **演算子の優先順位がはっきりしない式は括弧で囲む。** 意図と違う順に評価され、型変換エラーなどになる。
- **複数の文は `;` で区切る。**

## 変換と書き出し

```sql
COPY (FROM read_csv('in.csv')) TO 'out.parquet';  -- 拡張子で形式が決まる
COPY (FROM 'in.parquet') TO 'out.jsonl' (FORMAT json);
```

入力ファイルを上書きしない。書き出し先は別のパスにする。

## リモートのファイル

S3・R2・GCS・HTTPS上のファイルは、ダウンロードせずに読み込める。
認証と一覧の取り方は [references/remote.md](references/remote.md) を参照する。
