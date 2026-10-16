# self-review

[English](README.md)

自分のlocal変更 (未commit変更、または指定した1 commit) を敵対的にコードレビューし、検証を通過した指摘だけをチャットへ返す。変更を一時worktreeへsnapshotとして固定し、重点の異なる2つのFinder SubAgentと、specがあればContract SubAgentが指摘候補を探す。すべての候補は独立したVerifier SubAgentが反証を試み、確定した指摘だけを出力する。

GitHub、PR、CI、review threadは使わない。PRになった変更をレビューして投稿するには`github-pr-review`を使う。

## 使い方

- 「自分の変更を厳しくレビューして」
- 「このcommitをself reviewして」

```text
/self-review
/self-review HEAD~1
/self-review --spec 45
/self-review --spec docs/specs/login/spec.md
```

## 引数

| 引数              | 効果                                                                                                                             |
| ----------------- | -------------------------------------------------------------------------------------------------------------------------------- |
| `commit`          | レビューするcommit。省略時は未commit変更 (staged、unstaged、`.gitignore`対象外のuntracked)。                                     |
| `--spec <source>` | Contract軸のspec。GitHub Issue番号 (本文とmaintainerのコメントを使う)、またはspec contractを書いたMarkdownファイルのパスを渡す。 |

## 動作

- commit指定時は、そのcommitとfirst parentの差分だけを対象にする。root commit、branch全体の差分、GitHub PRは対象外。
- `scripts/self_review_snapshot.sh`がsnapshot用のworktreeを`/tmp/self-review.*`に作る。レビューはこのsnapshotだけを読み、ユーザーのworking treeは変更しない。
- Finderはsnapshotの検索と読み取りだけを行い、コマンドを実行しない。Verifierはsnapshot内で最小限のテストや再現コードを実行してよい。
- 候補は同じ場所または同じ根本原因のものを統合した後、1件ずつ検証する。`refuted`と`uncertain`は破棄する。確定はFinder、Contractの順で行い、Contractは先に確定した指摘と重複するものを破棄する。
- SubAgentが起動できない、または結果を返さない場合は中止し、原因を報告する。diffを自分で読んで代替レビューはしない。
- 出力の前に、snapshotがagentに変更されていないこと、未commit変更が対象なら元のworking treeもsnapshot作成時から変わっていないことを確かめる。どちらかが変わっていればレビュー結果を破棄し、再レビューが必要なことだけを報告する。
- Verdictは確定指摘が1件以上なら`CHANGES_REQUIRED`、0件なら`PASS`になる。結果はチャットへ出力し、ファイル保存やGitHubへの投稿はしない。
- snapshotは、中断した場合も含めて最後に削除する。元のrepositoryへreset、restore、stash、checkout、cleanは実行しない。

## 依存

- agent: [`code-reviewer-finder`](../../../agents/code-reviewer-finder.md)、[`code-reviewer-contract`](../../../agents/code-reviewer-contract.md)、[`code-reviewer-verifier`](../../../agents/code-reviewer-verifier.md)。Claude Code pluginとapmで配布される。`apm install -t codex`ではCodexのagent形式へ変換され、tools制限は失われる。その他の方法でinstallした場合は、同じpromptを汎用のSubAgentへ渡して代替する。
- `git`、`jq`、bash。`--spec`にIssue番号を渡す場合は`gh`

手順の詳細は[SKILL.md](SKILL.md)を参照。
