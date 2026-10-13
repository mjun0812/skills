# git-fix-conflict

[English](README.md)

進行中のmerge、rebase、cherry-pick、revert、`am`、`apply`で発生したコンフリクトを検出して解消する。進行中の操作が無くても、現在のbranchのPRが`CONFLICTING`の場合は、PRのbase branchをmergeして解消する。

進行中の操作を継続し、リポジトリのtest・lint・buildを実行したうえで、PRから検出した言語(PRが無ければ依頼とリポジトリ内の直近のcommitから判定)で結果を報告する。

## 使い方

- 「コンフリクトを直して」
- 「マージコンフリクトを解消して」

```text
/git-fix-conflict
/git-fix-conflict --dry-run
```

## 引数

| 引数        | 効果                                                                                                      |
| ----------- | --------------------------------------------------------------------------------------------------------- |
| `--dry-run` | コンフリクトファイル一覧と解消方針の提案のみを提示する。ファイル編集・`git add`・commit・pushは行わない。 |

## 動作

- branch、Git状態、進行中の操作、未解決ファイル(`git diff --name-only --diff-filter=U`)を確認する。コンフリクトが無ければ、その旨を報告して終了する。
- 未解決ファイルがあれば、進行中の操作を解消する。無い場合、PRが`CONFLICTING`ならfetchして`git merge origin/<base-branch>`で開始する。`--dry-run`ではmergeせず、`git merge-tree`で非破壊的に検出する。
- 各コンフリクトの両側を分析する。操作によってHEADとtheirsが指す側が入れ替わる点を踏まえて解消を適用し、判断理由を説明する。
- 解消したファイルをstageし、操作を完了させる(merge commit、`rebase --continue`、`cherry-pick --continue`、`revert --continue`、`am --continue`)。`apply`はstageまで行い、必要に応じてcommitする。
- リポジトリのテスト・lint・buildコマンドを実行し、失敗した場合は解消内容を見直す。
- PR branchへの反映が必要な場合はpushする。新規にrebaseを開始しない。履歴を書き換えるpushは事前にユーザーへ確認し、`--force`ではなく`--force-with-lease`のみを使う。
- 複雑なコンフリクト(大きなファイル、アーキテクチャの変更)は、自動で解消せずユーザーに判断を求める。
- 報告は[references/summary_template_ja.md](references/summary_template_ja.md)(英語は[references/summary_template.md](references/summary_template.md))に従う。

## 依存

- `git`と`gh` CLI

手順の詳細は[SKILL.md](SKILL.md)を参照。
