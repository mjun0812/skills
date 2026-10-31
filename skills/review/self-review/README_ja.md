# self-review

[English](README.md)

自分で書いた変更を敵対的にコードレビューし、検証を通過した指摘だけをチャットへ返す。PRの作成前後に、自分の変更を自己採点するために使う。対象はbranchの変更(baseとのmerge-base以降のcommitと未commit変更)を基本とし、引数を省略するとbranchの状態から対象を提案する。commitを指定すればその1 commitを対象にする。変更を一時worktreeへsnapshotとして固定し、重点の異なる2つのFinder SubAgentと、specがあればContract SubAgentが指摘候補を探す。すべての候補は独立したVerifier SubAgentが反証を試み、確定した指摘だけを出力する。

PRがあっても、レビューやcommentはGitHubへ投稿しない。PRを他人の立場でレビューして投稿するには`github-pr-review`を使う。

## 使い方

- 「自分の変更を厳しくレビューして」
- 「PRを出す前にself reviewして」
- 「このcommitをself reviewして」

```text
/self-review
/self-review --base origin/feat/parent
/self-review HEAD~1
/self-review --spec 45
/self-review --spec docs/specs/login/spec.md
```

## 引数

| 引数              | 効果                                                                                                                                                                           |
| ----------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `commit`          | レビューするcommit。指定時は対象を提案しない。                                                                                                                                 |
| `--base <ref>`    | branchの変更の起点。指定時は対象を提案せず、branchの変更をレビューする。省略時は現在のbranchのopen PRのbase branch、PRが無ければ`gh`が解決するrepositoryのdefault branch。     |
| `--spec <source>` | Contract軸のspec。GitHub Issue番号(本文とmaintainerのコメントを使う)、またはspec contractを書いたMarkdownファイルのパスを渡す。省略時はopen PR本文の`Closes #N`のIssueを使う。 |

## 動作

- `commit`と`--base`のどちらも指定しない場合は、baseより先のcommit数と未commit変更の有無から対象を決める。候補が1つなら質問せずに進み、複数あれば変更量を添えて選択肢を示す。branchの変更を推奨にする。

  | baseより先のcommit | 未commit変更 | 対象                                                      |
  | ------------------ | ------------ | --------------------------------------------------------- |
  | 0                  | なし         | 対象なしとして終了                                        |
  | 0                  | あり         | 未commit変更のみ                                          |
  | 1                  | なし         | branchの変更                                              |
  | 2以上              | なし         | branchの変更 / 最新commitのみ から選ぶ                    |
  | 1以上              | あり         | branchの変更 / 未commit変更のみ / 最新commitのみ から選ぶ |

- commitを省略すると、baseとHEADのmerge-baseからHEADまでのcommitと、未commit変更をまとめて対象にする。`--base`を省略した場合は、PRのbase repositoryを指すremoteからbase branchをfetchして使うので、fork構成でも古い`origin/main`をbaseにしない。open PRがあれば、そのタイトルと本文を変更目的としてSubAgentへ渡す。
- commit指定時は、そのcommitとfirst parentの差分だけを対象にする。root commit、checkoutしていないbranchやPRは対象外。
- `scripts/self_review_snapshot.sh`がsnapshot用のworktreeを`/tmp/self-review.*`に作る。レビューはこのsnapshotだけを読み、ユーザーのworking treeは変更しない。
- Finderはsnapshotの検索と読み取りだけを行い、コマンドを実行しない。Verifierはsnapshot内で最小限のテストや再現コードを実行してよい。
- 候補は同じ場所または同じ根本原因のものを統合した後、1件ずつ検証する。`refuted`と`uncertain`は破棄する。確定はFinder、Contractの順で行い、Contractは先に確定した指摘と重複するものを破棄する。
- SubAgentが起動できない、または結果を返さない場合は中止し、原因を報告する。diffを自分で読んで代替レビューはしない。
- 出力の前に、snapshotがagentに変更されていないことを確かめる。branchの変更が対象なら、元のrepositoryのHEADとworking treeがsnapshot作成時から変わっていないことも確かめる。どちらかが変わっていればレビュー結果を破棄し、再レビューが必要なことだけを報告する。
- `hunk`があれば、指摘を対象差分の上にnoteとして表示する。このrepositoryのhunk sessionがあればその表示を対象差分へ切り替え、無ければHerdrのpaneでhunkを起動する。以前のself-reviewが付けたnoteだけを消し、他のagentやユーザーが付けたnoteは残す。diffのhunk外を指す指摘はhunkには表示せず、件数だけを報告する。hunk sessionが無く、Herdr外で実行している場合はhunkへの表示をスキップする。
- Verdictは確定指摘が1件以上なら`CHANGES_REQUIRED`、0件なら`PASS`になる。hunkへ表示した場合も、すべての指摘をチャットへ出力する。ファイル保存やGitHubへの投稿はしない。
- snapshotは、中断した場合も含めて最後に削除する。元のrepositoryへreset、restore、stash、checkout、cleanは実行しない。hunkのsessionとpaneは残す。

## 依存

- agent: [`code-reviewer-finder`](../../../agents/code-reviewer-finder.md)、[`code-reviewer-contract`](../../../agents/code-reviewer-contract.md)、[`code-reviewer-verifier`](../../../agents/code-reviewer-verifier.md)。Claude Code pluginとapmで配布される。`apm install -t codex`ではCodexのagent形式へ変換され、tools制限は失われる。その他の方法でinstallした場合は、同じpromptを汎用のSubAgentへ渡して代替する。
- `git`、`jq`、bash。PRの情報や`--spec`のIssueを読むには`gh`
- 任意: [`hunk`](https://github.com/modem-dev/hunk)。hunk sessionが無いときにpaneを開くには[Herdr](https://github.com/herdrdev/herdr)

手順の詳細は[SKILL.md](SKILL.md)を参照。
