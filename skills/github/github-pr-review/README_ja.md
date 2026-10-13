# github-pr-review

[English](README.md)

GitHubのPull Requestを敵対的にコードレビューし、検証を通過した指摘だけをレビューレポートとinline commentで投稿する。PR headのsnapshot worktreeを対象に、重点の異なる2つのFinder SubAgent、Standards SubAgent、specがあればContract SubAgentが指摘候補を探す。すべての候補は独立したVerifier SubAgentが反証を試み、確定した指摘だけを投稿する。self reviewにも対応する。

specは`--spec`、またはPR本文の`Closes #N`のIssueから解決する。どちらも無ければContract軸をスキップし、レポートにその旨を書く。PRになっていないlocalの変更をレビューするには`self-review`を使う。

## 使い方

- 「このPRをレビューして」

```text
/github-pr-review
/github-pr-review 123
/github-pr-review 123 --spec 45
/github-pr-review 123 --dry-run
```

## 引数

| 引数             | 効果                                                               |
| ---------------- | ------------------------------------------------------------------ |
| `PR number`      | レビューするPR。省略時は現在のbranchのPR。無ければ確認する。       |
| `--spec <issue>` | Contract軸のspecとして使うIssue。PRの`Closes`のIssueより優先する。 |
| `--dry-run`      | レポートの提示のみ。投稿、dismiss、resolveは行わない。             |

## 動作

- 1回の実行で扱うPRは1件だけ。PR headを専用worktreeにdetachedでcheckoutし、レビューはこのsnapshotだけを読む。
- 候補は同じ場所または同じ根本原因のものを統合した後、1件ずつ検証する。`refuted`と`uncertain`は破棄する。確定はFinder、Standards、Contractの順で行い、後の軸は先に確定した指摘と重複するものを破棄する。
- SubAgentが起動できない、または結果を返さない場合は、投稿、dismiss、resolveをせずに中止し、原因を報告する。diffを自分で読んで代替レビューはしない。
- 失敗したCIの結果はFinderの証拠として使い、レポートの概要にも記載する。
- レポートの言語(`ja`または`en`)は、PRのタイトルと本文から`scripts/render_review.py`が決める。同scriptがfindings JSON(形式は`references/findings.md`)からレビュー本文とinline commentを生成する。Verdictは確定指摘が1件以上なら`REQUEST_CHANGES`、0件なら`APPROVE`になる。
- 投稿は`scripts/post_review.sh`で行う。diffに含まれない`(path, line, side)`のinline commentは除外される。本文とcommentはファイルで渡す。
- self reviewでは、自分のPRにはapproveやrequest changesを投稿できないため、`COMMENT` eventで投稿する。本文のVerdict表記は変えない。
- 投稿に成功した後に限り、同じreviewerの以前のreviewをdismiss(`scripts/dismiss_my_reviews.sh`)し、そのthreadをresolve(`scripts/resolve_review_threads.sh`)する。投稿に失敗した場合は何もしない。
- レビュー中にPRのheadが進んだ場合は、確定指摘をレビューしたcommitに対する`COMMENT`として投稿し、以前のreviewには手を付けない。指摘が0件なら何も投稿しない。
- worktree、一時ref、一時directoryは、中断した場合も含めて最後に削除する。
- public repositoryへ投稿するレビューには、private repositoryの情報を書かない。

## 依存

- agent: [`code-reviewer-finder`](../../../agents/code-reviewer-finder.md)、[`code-reviewer-standards`](../../../agents/code-reviewer-standards.md)、[`code-reviewer-contract`](../../../agents/code-reviewer-contract.md)、[`code-reviewer-verifier`](../../../agents/code-reviewer-verifier.md)。Claude Code pluginとapmで配布される。`apm install -t codex`ではCodexのagent形式へ変換され、tools制限は失われる。その他の方法でinstallした場合は、同じpromptを汎用のSubAgentへ渡して代替する。
- `git`、`gh`、`jq`、Python

手順の詳細は[SKILL.md](SKILL.md)を参照。
