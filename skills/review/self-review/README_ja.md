# self-review

[English](README.md)

自分で書いた変更を敵対的にコードレビューし、検証を通過した指摘だけをチャットへ返す。PRの作成前後に、自分の変更を自己採点するために使う。対象はbranchの変更(baseとのmerge-base以降のcommitと未commit変更)を基本とし、引数を省略するとbranchの状態から対象を提案する。commitを指定すればその1 commitを対象にする。変更を一時worktreeへsnapshotとして固定し、重点の異なる2つのFinder SubAgentが指摘候補を探す。PRがあれば、Claim SubAgentがPR本文の主張を実コードで確かめる。すべての候補は独立したVerifier SubAgentが実コードを実行して反証を試みる。再現できた指摘を要修正として、再現はできないが反証も無い指摘を未証明として出力する。

PRがあっても、レビューやcommentはGitHubへ投稿しない。PRを他人の立場でレビューして投稿するには`github-pr-review`を使う。

## 使い方

- 「自分の変更を厳しくレビューして」
- 「PRを出す前にself reviewして」
- 「このcommitをself reviewして」

```text
/self-review
/self-review --base origin/feat/parent
/self-review HEAD~1
```

## 引数

| 引数           | 効果                                                                                                                                                                       |
| -------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `commit`       | レビューするcommit。指定時は対象を提案しない。                                                                                                                             |
| `--base <ref>` | branchの変更の起点。指定時は対象を提案せず、branchの変更をレビューする。省略時は現在のbranchのopen PRのbase branch、PRが無ければ`gh`が解決するrepositoryのdefault branch。 |

## 動作

- `commit`と`--base`のどちらも指定しない場合は、baseより先のcommit数と未commit変更の有無から対象を決める。候補が1つなら質問せずに進み、複数あれば変更量を添えて選択肢を示す。branchの変更を推奨にする。

  | baseより先のcommit | 未commit変更 | 対象                                                      |
  | ------------------ | ------------ | --------------------------------------------------------- |
  | 0                  | なし         | 対象なしとして終了                                        |
  | 0                  | あり         | 未commit変更のみ                                          |
  | 1                  | なし         | branchの変更                                              |
  | 2以上              | なし         | branchの変更 / 最新commitのみ から選ぶ                    |
  | 1以上              | あり         | branchの変更 / 未commit変更のみ / 最新commitのみ から選ぶ |

  HEADがmerge commitの場合は、取り込んだ他人の変更をレビューしないよう「最新commitのみ」を選択肢から外す。

- commitを省略すると、baseとHEADのmerge-baseからHEADまでのcommitと、未commit変更をまとめて対象にする。`--base`を省略した場合は、PRのbase repositoryを指すremoteからbase branchをfetchして使うので、fork構成でも古い`origin/main`をbaseにしない。ただし、PRがまだ無く`upstream` remoteも無いforkでは、`gh`がfork自身を返すため`origin/main`がbaseになる。対象がbranchの変更でopen PRがあれば、そのタイトルと本文を変更目的としてSubAgentへ渡す。remoteが無い、offlineなどでbaseを解決できない場合は、未commit変更があれば未commit変更のみをレビューし、無ければ`--base`の指定を求める。
- commit指定時は、そのcommitとfirst parentの差分だけを対象にする。root commit、checkoutしていないbranchやPRは対象外。
- `scripts/self_review_snapshot.sh`がsnapshot用のworktreeを`/tmp/self-review.*`に作る。レビューはこのsnapshotだけを読み、ユーザーのworking treeは変更しない。
- 最初に、変更の説明、commit、diffから変更の意図を2〜3文で言い直し、SubAgentへ渡す。指摘は、この意図が破られるかどうかで判定される。意図を1つに決められない場合はユーザーに確認する。
- Finder、Claim、Verifierは、テストや再現コードを実行してよい。実行は、各SubAgentがsnapshotから一時ディレクトリへ書き出した実行用コピーで行い、snapshotのファイルは変更しない。Finderは指摘ごとに、そのまま実行できる再現のコマンド列と出力を添える。
- Claimは、PRのタイトルと本文を変更目的として使う場合だけ起動する。PR本文が述べる検証の結果、範囲、影響範囲を実行して確かめ、説明と実際の結果との食い違いを候補にする。説明とコードのどちらが正しいかは判定しない。
- 候補は同じ場所または同じ根本原因のものを統合した後、1件ずつ検証する。Verifierは再現のコマンド列を自分で実行し直す。`refuted`と`uncertain`は破棄し、件数だけを報告する。確定した指摘のうち、Verifierが再現できたものを要修正、コードを読んで到達を確かめただけのものを未証明に分ける。確定はFinder、Claimの順で行い、Claimは先に確定した指摘と重複するものを破棄する。
- SubAgentが起動できない、または結果を返さない場合は中止し、原因を報告する。diffを自分で読んで代替レビューはしない。
- 出力の前に、snapshotがagentに変更されていないことを確かめる。branchの変更か未commit変更のみが対象なら、元のrepositoryのHEADとworking treeがsnapshot作成時から変わっていないことも確かめる。どちらかが変わっていればレビュー結果を破棄し、再レビューが必要なことだけを報告する。
- `hunk`があれば、指摘を対象差分の上にnoteとして表示する。このrepositoryのhunk sessionがあればその表示を対象差分へ切り替え、無ければHerdrのpaneでhunkを起動する。以前のself-reviewが付けたnoteだけを消し、他のagentやユーザーが付けたnoteは残す。以前のnoteでも、返信が付いているものは消さずに残す。diffのhunk外を指す指摘はhunkには表示せず、件数だけを報告する。hunk sessionが無く、Herdr外で実行している場合と、hunk sessionが無く指摘も0件の場合は、hunkへの表示をスキップする。
- Verdictは要修正の指摘が1件以上なら`CHANGES_REQUIRED`、0件なら`PASS`になる。未証明の指摘はVerdictを変えない。hunkへ表示した場合も、すべての指摘をチャットへ出力する。ファイル保存やGitHubへの投稿はしない。
- 最後にsnapshotのcleanupを試みる。作成時のHEAD、ファイル内容、indexから変化がなく、新しいuntracked fileもない場合だけ、初期入力のコピーをsnapshot内でrestoreしてから`git worktree remove`で削除する。調査中の編集、新しいcommit、削除拒否があればworktreeを残し、パスと理由を報告する。作成失敗時の部分的なworktree、親ディレクトリ、レビュー資料も残す。拒否された削除を別の方法で実行しない。元のrepositoryへreset、restore、stash、checkout、cleanは実行しない。hunkのsessionとnote、hunkを起動したpaneは残す。

## 依存

- agent: [`code-reviewer-finder`](../../../agents/.apm/agents/code-reviewer-finder.md)、[`code-reviewer-claim`](../../../agents/.apm/agents/code-reviewer-claim.md)、[`code-reviewer-verifier`](../../../agents/.apm/agents/code-reviewer-verifier.md)。Claude Code pluginとapmで配布される。`apm install -t codex`ではCodexのagent形式へ変換され、tools制限は失われる。その他の方法でinstallした場合は、同じpromptを汎用のSubAgentへ渡して代替する。
- `git`、`jq`、bash。`--base`を省略したときのbaseの解決とPRの情報の取得には`gh`
- 任意: [`hunk`](https://github.com/modem-dev/hunk)。hunk sessionが無いときにpaneを開くには[Herdr](https://github.com/herdrdev/herdr)

手順の詳細は[SKILL.md](SKILL.md)を参照。
