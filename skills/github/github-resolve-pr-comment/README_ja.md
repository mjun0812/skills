# github-resolve-pr-comment

[English](README.md)

PRのレビューコメントを確認し、対応方針を決めてコードを修正し、返信するSkill。inline review thread、review summary body、PR-level issue commentの3種類をすべて対象にする。各コメントをMust Fix、Should Fix、質問、情報共有に分類し、修正をcommit・pushして、未解決の全inline threadへ返信する。GitHubへ投稿するのはこの返信だけで、全コメントの対応結果は対応サマリーとしてチャットに表示する。

「レビューコメントが来たので対応して」のような依頼は、本skillを呼ぶ[`github-pr-fix`](../github-pr-fix/README_ja.md)が受ける。本skillは、名前で指定したときと、現在の作業ツリーでレビューコメントだけに対応させるときに使う。

## 使い方

- 「github-resolve-pr-commentでレビューコメントに対応して」
- 「このworktreeでレビューコメントだけに対応して」

```text
/github-resolve-pr-comment
/github-resolve-pr-comment 123 --dry-run
```

## 引数

| 引数        | 効果                                                                           |
| ----------- | ------------------------------------------------------------------------------ |
| `PR number` | 対応するPR。省略時は現在のbranchのPR。                                         |
| `--dry-run` | 分類結果と対応方針のみを提示する。ファイル編集、commit、push、返信は行わない。 |

## 動作

- 対応単位は未解決のthread(`isResolved=false`)で、reviewのstateや`isOutdated`では除外しない。解決済みのthreadはスキップする。
- 同じ話題は1件にまとめ、inline threadを優先する。同じreviewerが明示的に撤回した指摘は除外する。
- Must Fixは修正する。修正できない場合は技術的な理由を返信する。Should Fixは採否を判断し、理由を添えて返信する。質問には回答し、情報共有は必要に応じて確認済みと返信する。
- コード変更はPRの言語(タイトルと本文から検出し、曖昧なら英語)のcommit messageでcommit・pushする。コード変更が無ければcommitとpushはスキップする。
- inline threadへの返信は、threadの先頭commentに対して`scripts/post_review_reply.sh`で投稿する。本文は必ずファイルで渡す。
- review summary bodyとPR-level issue commentには、GitHub上で返信しない。対応結果は対応サマリーに記載する。
- 対応サマリーは`references/comment_summary_template.md`または`_ja`に従い、最終出力としてチャットに表示する。GitHubへは投稿しない。
- commentの意図が不明確な場合や大きな設計変更が必要な場合は、実行前にユーザーへ確認する。

## 依存

- `git`と`gh` CLI

手順の詳細は[SKILL.md](SKILL.md)を参照。
