# github-pr-review

[English](README.md)

GitHubのPull Requestを敵対的にコードレビューし、検証を通過した指摘だけをレビューレポートとinline commentで投稿する。投稿前に内容を確認し、`--auto`を付けると確認せずに投稿する。PR headのsnapshot worktreeを対象に、重点の異なる2つのFinder SubAgentが指摘候補を探し、Claim SubAgentがPR本文の主張を実コードで確かめる。すべての候補は独立したVerifier SubAgentが実コードを実行して反証を試みる。再現できた指摘を要修正事項として、再現はできないが反証も無い指摘を未証明の指摘として投稿する。self reviewにも対応する。

自分の変更を投稿せずに自己採点するには`self-review`を使う。

## 使い方

- 「このPRをレビューして」

```text
/github-pr-review
/github-pr-review 123
/github-pr-review 123 --auto
```

## 引数

| 引数        | 効果                                                         |
| ----------- | ------------------------------------------------------------ |
| `PR number` | レビューするPR。省略時は現在のbranchのPR。無ければ確認する。 |
| `--auto`    | 投稿前の確認を省き、そのまま投稿する。                       |

## 動作

- 1回の実行で扱うPRは1件だけ。PR headを専用worktreeにdetachedでcheckoutし、レビューはこのsnapshotだけを読む。
- レビュー範囲は`scripts/resolve_review_range.sh`が決める。base branchとのmerge-baseからPR headまでを対象にし、未mergeの別のopen PRに積み上げたPRでは、そのPRのheadから先だけを対象にする。diffなどの大きな入力は一時directoryのファイルでSubAgentへ渡す。
- 最初に、PRのタイトルと本文、commit、diffから変更の意図を2〜3文で言い直し、SubAgentへ渡す。指摘は、この意図が破られるかどうかで判定される。
- Finder、Claim、Verifierは、テストや再現コードを実行してよい。実行は、各SubAgentがsnapshotから一時ディレクトリへ書き出した実行用コピーで行い、snapshotのファイルは変更しない。Finderは指摘ごとに、そのまま実行できる再現のコマンド列と出力を添える。
- Claimは、PR本文が述べる検証の結果、範囲、影響範囲を実行して確かめ、説明と実際の結果との食い違いを候補にする。説明とコードのどちらが正しいかは判定しない。
- 候補は同じ場所または同じ根本原因のものを統合した後、1件ずつ検証する。Verifierは再現のコマンド列を自分で実行し直す。`refuted`と`uncertain`は破棄し、件数だけをチャットへ報告する。確定した指摘のうち、Verifierが再現できたものを要修正事項、コードを読んで到達を確かめただけのものを未証明の指摘に分ける。確定はFinder、Claimの順で行い、Claimは先に確定した指摘と重複するものを破棄する。
- SubAgentが起動できない、または結果を返さない場合は、投稿、dismiss、resolveをせずに中止し、原因を報告する。diffを自分で読んで代替レビューはしない。
- 失敗したCIの結果はFinderの証拠として使い、レポートの概要にも記載する。
- 同じPRに以前投稿した指摘と返信を、resolve済みも含めて`scripts/fetch_prior_findings.sh`で取得し、SubAgentへ渡す。見送りか却下で決着した指摘と同じ根本原因の候補は、判断の前提が変わったことを示せない限り検証の前に破棄し、蒸し返さない。
- レポートの言語(`ja`または`en`)は、PRのタイトルと本文から`scripts/render_review.py`が決める。同scriptがfindings JSON(形式は`references/findings.md`)から、チャット用の全文レポート、inline comment、GitHubへ投稿するreview本文を生成する。review本文は指摘の一覧表で、各行が詳細を載せたinline commentへリンクする。Verdictは要修正事項が1件以上なら`REQUEST_CHANGES`、0件なら`APPROVE`になる。未証明の指摘は、レポートとinline commentに載るが、Verdictを変えない。要修正事項には、再現のコマンド列と出力を載せる。
- 投稿前に、Verdict、全文レポート、dismiss・resolveの件数を提示し、投稿・修正して再提示・キャンセルを確認する。`--auto`ではこの確認を省く。
- 投稿は`scripts/post_review.sh`で行う。inline commentを下書きのreviewとして先に作り、そのURLへリンクする一覧表を本文にして公開する。公開前に失敗した場合は下書きを削除する。diffに含まれない`(path, line, side)`の指摘はinline commentにできないため、詳細をreview本文に載せる。
- self reviewでは、自分のPRにはapproveやrequest changesを投稿できないため、`COMMENT` eventで投稿する。本文のVerdict表記は変えない。
- 投稿に成功した後に限り、同じreviewerの以前のreviewをdismiss(`scripts/dismiss_my_reviews.sh`)し、そのthreadをresolve(`scripts/resolve_review_threads.sh`)する。投稿に失敗した場合は何もしない。
- レビュー中にPRのheadが進んだ場合は、確定指摘をレビューしたcommitに対する`COMMENT`として投稿し、以前のreviewには手を付けない。指摘が0件なら何も投稿しない。
- worktree、一時ref、一時directoryは、中断した場合も含めて最後に削除する。
- public repositoryへ投稿するレビューには、private repositoryの情報を書かない。

## 依存

- agent: [`code-reviewer-finder`](../../../agents/.apm/agents/code-reviewer-finder.md)、[`code-reviewer-claim`](../../../agents/.apm/agents/code-reviewer-claim.md)、[`code-reviewer-verifier`](../../../agents/.apm/agents/code-reviewer-verifier.md)。Claude Code pluginとapmで配布される。`apm install -t codex`ではCodexのagent形式へ変換され、tools制限は失われる。その他の方法でinstallした場合は、同じpromptを汎用のSubAgentへ渡して代替する。
- `git`、`gh`、`jq`、Python

手順の詳細は[SKILL.md](SKILL.md)を参照。
