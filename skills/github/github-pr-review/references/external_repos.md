# 外部repositoryの参照

本文で投稿先以外のrepositoryを識別子 (`owner/repo`、`owner/repo#N`、GitHub URL、branch名) で参照する場合は、書く前に参照先と投稿先の公開状態を確認する。会話中に見た事実であっても、確認せずに書かない。`#N` だけの参照は投稿先のIssue/PRなので対象外。

## 判定

```bash
gh repo view --json owner,visibility --jq '[.owner.login, .visibility] | @tsv'
gh repo view <owner/repo> --json owner,visibility --jq '[.owner.login, .visibility] | @tsv'
```

| 参照先                          | 投稿先                 | owner    | 扱い             |
| ------------------------------- | ---------------------- | -------- | ---------------- |
| `PUBLIC`                        | 問わない               | 問わない | 識別子のまま書く |
| `PRIVATE` / `INTERNAL`          | `PRIVATE` / `INTERNAL` | 同じ     | 識別子のまま書く |
| `PRIVATE` / `INTERNAL`          | `PUBLIC`               | 問わない | 匿名化           |
| `PRIVATE` / `INTERNAL`          | `PRIVATE` / `INTERNAL` | 異なる   | 匿名化           |
| 取得失敗 (権限なし・存在しない) | 問わない               | 問わない | 匿名化           |

## 匿名化

- 識別子を書かず、「既存のreviewを書き直した」「別のrepositoryで同じ問題が起きた」のように参照先を特定できない表現にする
- repository名だけでなく、Issue/PR番号、URL、branch名、参照先固有のファイルパスや固有名詞も書かない
- 参照先で確認した事実そのもの (問題の内容、検証結果) は残してよい
