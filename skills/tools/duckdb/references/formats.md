# 拡張が必要な形式

CSV・JSON・Parquet以外の形式は、拡張を使って読み書きする。
多くの拡張は初回の使用時に自動で読み込まれるが、「先頭に書く」列に指定がある形式は、明示して `LOAD` しないと関数が見つからないエラーになる。

| 形式                                          | 拡張      | 読み方                                                                                                                                         | 書き出し (`COPY ... TO`)                                              | 先頭に書く                   |
| --------------------------------------------- | --------- | ---------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------- | ---------------------------- |
| Excel (`.xlsx`)                               | `excel`   | `read_xlsx('x.xlsx')`、または `FROM 'x.xlsx'`                                                                                                  | `(FORMAT xlsx, HEADER true)`                                          | 書き出しのとき `LOAD excel;` |
| SQLite (`.db`・`.sqlite`)                     | `sqlite`  | `ATTACH 'x.sqlite' AS s (TYPE sqlite);` で開いて `SHOW ALL TABLES;` でテーブルを確かめる。1テーブルだけ読むなら `sqlite_scan('x.sqlite', 't')` | `ATTACH` したDBへ `CREATE TABLE s.t AS ...`                           | 不要                         |
| 地理データ (`.geojson`・`.gpkg`・`.shp` など) | `spatial` | `ST_Read('x.gpkg')`                                                                                                                            | `(FORMAT GDAL, DRIVER 'GeoJSON')` (`'GPKG'`・`'ESRI Shapefile'` など) | 読み書きとも `LOAD spatial;` |
| Avro (`.avro`)                                | `avro`    | `read_avro('x.avro')`                                                                                                                          | `(FORMAT avro)`                                                       | 不要                         |

- Excelへの書き出しは、`HEADER true` を付けないと列名が出力されない。整数の列は、読み込むと `DOUBLE` になる。
- SQLiteのファイルは `FROM 'x.sqlite'` では読めない。
- 拡張が未installなら、`LOAD` の前に `INSTALL <拡張>;` を書く。

ここに無い形式や指定は、[docs-search.md](docs-search.md) の手順で公式docsを引く。
