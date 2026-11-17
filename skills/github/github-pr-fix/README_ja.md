# github-pr-fix

[English](README.md)

PRをmerge可能な状態へ戻すSkill。コンフリクト、CI失敗、未対応のレビューコメントを検出し、該当するものに対応するサブSkillだけを実行する。作業はPR headから作る専用worktree内で行い、修正はPR head branchへpushする。

1種類の問題だけを直す場合は、そのskillを直接使う。[`git-fix-conflict`](../../git/git-fix-conflict/README_ja.md)、[`github-fix-ci`](../github-fix-ci/README_ja.md)、[`github-resolve-pr-comment`](../github-resolve-pr-comment/README_ja.md)。

## 使い方

- 「PRの問題を全部直して」
- 「PRをまとめて修正して」

```text
/github-pr-fix
/github-pr-fix 123
```

## 引数

| 引数        | 効果                                   |
| ----------- | -------------------------------------- |
| `PR number` | 修正するPR。省略時は現在のbranchのPR。 |

## 動作

- PRが見つからない場合や、pushできないforkのPRの場合は、エラーで中止する。
- worktreeは`<repo-root>/.tmp/<repo-name>-worktrees/pr-<number>-fix`に、fetch済みのPR head refから作るlocal branch `pr-fix/<number>`として作成する。同名worktreeやlocal branchがある場合は、既存の作業を残して中止する。
- PRの言語はタイトルと本文から1回だけ検出し(曖昧なら英語)、すべてのサブSkillと最終サマリーに引き継ぐ。
- 検出は並列に行う。コンフリクトはPRが`CONFLICTING`の場合、CIはcheckに`FAILURE`、`CANCELLED`、`TIMED_OUT`がある場合、レビューコメントは未解決のinline threadが1件以上ある場合に対応する。threadの数は`scripts/fetch_review_threads.sh --only-unresolved`で数える。
- サブSkillは`git-fix-conflict`、`github-fix-ci`、`github-resolve-pr-comment`の順に実行し、前のステップが失敗しても後続を試みる。大きな変更の前にはユーザーに確認する。
- pushは`git push <push-remote> HEAD:<head-ref-name>`でPR head branchへ明示的に行う。cross repository PRでは、`origin`ではなくhead repositoryへpushする。
- 元の作業ツリーは編集しない。最後に未commit変更と未pushのcommitを確認し、PRの最終状態をサマリー(templateは`references/summary_template.md`と`_ja`)で表示する。
- 正常完了し、変更がすべてPR headへpush済みの場合だけ、今回作ったworktreeを`git worktree remove`で削除する。成功後にlocal branchを`git branch -d`で削除し、一時refを片付ける。エラー、中止、未commit変更、未pushのcommit、削除拒否の場合はworktreeとbranchを残し、パスと理由を報告する。親ディレクトリや他のworktreeは削除せず、拒否された削除を別の方法で実行しない。

## 依存

- skill: [`git-fix-conflict`](../../git/git-fix-conflict/README_ja.md)、[`github-fix-ci`](../github-fix-ci/README_ja.md)、[`github-resolve-pr-comment`](../github-resolve-pr-comment/README_ja.md)
- `git`と`gh` CLI

手順の詳細は[SKILL.md](SKILL.md)を参照。
