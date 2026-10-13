# git-squash

[English](README.md)

現在のbranchのcommitを、対話を最小化してsquash・整理し、`--no-push`が無ければ`--force-with-lease`でpushする。未指定時は論理単位に自動でグルーピングし、`--one`指定時は全commitを1つにまとめる。

新しいcommitメッセージはConventional Commits形式で、指定した言語で記述する。

## 使い方

- 「commitをsquashして」
- 「commitを整理して」

```text
/git-squash
/git-squash ja --one
/git-squash --no-push
/git-squash --dry-run
```

## 引数

| 引数          | 効果                                                                                                |
| ------------- | --------------------------------------------------------------------------------------------------- |
| `language`    | commitメッセージと報告の言語(`ja`、`en`)。デフォルトは英語。                                        |
| `--one`, `-1` | 対象commitを1つにsquashする。                                                                       |
| `--no-push`   | squash後にpushせず、必要なコマンドを報告する。                                                      |
| `--dry-run`   | squash計画(グルーピング案と新しいcommitメッセージ案)のみを提示する。reset・commit・pushは行わない。 |

## 動作

- 現在のbranch、base branch、対象commit数、作業ツリー状態、upstreamとの差分を事前に確認する。
- default branch上、対象commitが0件、未commit変更あり(stashやcommitは自動実行しない)、upstreamに未取得commitありのいずれかなら、何も変更せず中止する。commitが1件のみならsquash不要として終了する。
- `--one`が無い場合は、commitのtype、変更ファイル、PR文脈から論理単位にグルーピングする。グループ分離が不安定な場合や、同一ファイルの変更を安全に分離できない場合は、1つのcommitにまとめる。
- Conventional Commits形式で、2行目を空行、3行目以降を箇条書きとしてメッセージを生成する。
- `git reset --soft origin/<base-branch>`で対象commitを解除し、commitを作り直す。
- `git push --force-with-lease`を自動実行する。失敗した場合は中止し、`--force`へフォールバックしない。
- ユーザー確認は行わない。危険な状態は理由を報告して中止する。
- 報告は[references/summary_template_ja.md](references/summary_template_ja.md)(英語は[references/summary_template.md](references/summary_template.md))に従う。

## 依存

- `git`と`gh` CLI

手順の詳細は[SKILL.md](SKILL.md)を参照。
