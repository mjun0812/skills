# duckdb

[English](README.md)

DuckDB CLIで、レコードの集まりからなるデータファイル (JSONL・CSV・TSV・Parquet・レコード配列のJSON、agentのsessionログなど) を、schemaを確かめてから集計・点検・変換・結合する。

データファイルの件数・分布・キーや型・重複や欠損を調べるとき、複数ファイルを横断して集計するとき、形式を変換するとき、またはそのためにPython・awkのscriptを書こうとしたときに使う。S3・GCS・HTTPS上のファイルや、DuckDBの仕様確認にも使う。単一のJSONオブジェクト (設定やAPIレスポンス) から値を取り出すだけの場合 (jqで足りる) や、ファイルの編集には使わない。

## 使い方

- 「このJSONLにどんなキーがあって、重複や型の揺れがないか確認して」
- 「sessionログからtoolごとのエラー率を出して」
- 「この実験結果のCSVをmodelごとに平均して」
- 「このCSVをParquetに変換して」

## 動作

- 集計の前に `DESCRIBE` / `SUMMARIZE` でschemaを確かめ、確かめた列名と型でSQLを書く。型が揃わない列は `json_type()` で内訳を見る。
- 出力は `-csv` か `-markdown` にし、集計や `LIMIT` で必要な行だけを出す。
- 列の違うCSVは `union_by_name`、レコードごとに形が違うJSONLは `from_json` と `unnest` で読む。
- SQLを書くときの注意 (別名には `AS` を付ける、優先順位がはっきりしない式は括弧で囲む、文を `;` で区切る) を持つ。
- DuckDB固有の関数やオプションは、書く前にDuckDB公式の全文検索indexを手元にcacheして検索する ([references/docs-search.md](references/docs-search.md))。
- Excel・SQLite・地理データ・Avroは、必要な拡張と読み書きの指定を表で確かめる ([references/formats.md](references/formats.md))。
- S3・R2・GCS・HTTPS上のファイルは、ダウンロードせずに読む ([references/remote.md](references/remote.md))。

## 依存

- `duckdb` CLI
- docs検索とリモートのファイルには、DuckDBの `httpfs` と `fts` extension (初回に自動でinstallされる)

## 出典

[duckdb/duckdb-skills](https://github.com/duckdb/duckdb-skills) (MIT License) の `read-file`・`query`・`convert-file`・`duckdb-docs`・`s3-explore` を1つにまとめ、agentが作業の途中で使う形に書き直した。docs検索の手順とリモートのファイルの読み方は、それぞれ `duckdb-docs` と `s3-explore` をもとにしている。

手順の詳細は[SKILL.md](SKILL.md)を参照。
