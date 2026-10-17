# リモートのファイルを読む

S3・R2・GCS・HTTPS上のファイルは、ダウンロードせずに `FROM` へURLを書いて読める。Parquetなら条件で絞った分だけ転送される。

## 認証

先頭で `LOAD httpfs;` し、置き場所に合うsecretを作る。公開bucketとHTTPSのURLにはsecretは要らない。

| 置き場所      | URL                    | secret                                                                               |
| ------------- | ---------------------- | ------------------------------------------------------------------------------------ |
| AWS S3        | `s3://`                | `CREATE SECRET (TYPE S3, PROVIDER credential_chain);`                                |
| Cloudflare R2 | `r2://`                | `CREATE SECRET (TYPE R2, PROVIDER credential_chain);`                                |
| GCS           | `gs://`, `gcs://`      | `CREATE SECRET (TYPE GCS, PROVIDER credential_chain);`                               |
| MinIOなど     | `s3://` + 独自endpoint | `CREATE SECRET (TYPE S3, KEY_ID '...', SECRET '...', ENDPOINT '...', USE_SSL true);` |

## 中身を調べる

一覧は `read_blob` で取る。`content` 列を選ぶとファイルの中身まで転送されるので、名前・サイズ・更新日時だけを選ぶ。

```sql
LOAD httpfs;
CREATE SECRET (TYPE S3, PROVIDER credential_chain);
SELECT filename, (size / 1024 / 1024)::DECIMAL(10, 1) AS size_mb, last_modified
FROM read_blob('s3://bucket/prefix/*')
ORDER BY filename LIMIT 50;
```

ファイルのschemaと件数は、ローカルと同じく `DESCRIBE FROM 's3://bucket/x.parquet'` と `count(*)` で確かめる。Parquetの行数とサイズはmetadataだけで分かる。

```sql
SELECT file_name, sum(row_group_num_rows) AS total_rows,
       (sum(row_group_compressed_bytes) / 1024 / 1024)::DECIMAL(10, 1) AS compressed_mb
FROM parquet_metadata('s3://bucket/prefix/*.parquet')
GROUP BY file_name;
```
