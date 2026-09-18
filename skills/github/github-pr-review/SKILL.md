---
name: github-pr-review
description: >-
  GitHubのPull Requestを敵対的にコードレビューし、検証を通過した指摘だけをレビューレポートとinline commentで投稿するSkill。`--spec` またはPRに紐づくIssueからspecを解決できる場合は、specとの整合も検査する。self reviewにも対応する。
  ユーザーが「このPRをレビューして」のように依頼したら使うこと。
allowed-tools: Task, Read, Write, AskUserQuestion, Bash(git:*), Bash(gh:*), Bash(jq:*), Bash(mkdir:*), Bash(mktemp:*), Bash(rm:*), Bash(bash:*), Bash(python:*)
---

# Pull Request Review

PRのhead commitを worktree にチェックアウトし、Finder SubAgentが指摘候補を探す。
Finder SubAgentが出した指摘候補は、1件ずつ Verifier SubAgent が反証を試み、
検証を通過したものだけを要修正事項としてレビューレポートとinline commentに投稿する。
並行して Standards SubAgent がmergeをブロックすべき規約違反・コードスメルの指摘候補を探し、1件ずつ Verifier の検証を経たものだけを同じレビューに含める。
spec sourceを解決できる場合は、Contract SubAgent がspecとの不整合の指摘候補を第3の軸として探し、同じくVerifierの検証を経たものだけをレビューに含める。

## Arguments

- `PR number`: レビューするPR番号 (optional, defaults to PR for current branch)
- `--spec <issue-number>`: Contract reviewに使うspecのGitHub Issue番号。指定時は関連Issueより優先する
- `--dry-run`: 生成したレポート本文をチャットに提示するのみで、`post_review.sh` 等の投稿スクリプト・dismiss・resolve操作を一切呼ばない(worktreeの後片付けは通常どおり行う)

## Task

### Phase 1: 準備

#### Phase 1.1: 対象PRの特定

- **引数にPR番号が指定されている場合**: 指定されたPRを対象にする
- **引数なし**
  - **現在のブランチに紐づくopen PRが存在する場合**: そのPRをそのまま使用する(確認なし)
  - **現在のブランチに紐づくopen PRが存在しない場合**: RemoteのOpen PR一覧を取得し、`AskUserQuestion`でユーザーに対象PRを確認する。Open PRが1件もなければその旨を報告して終了する

#### Phase 1.2: PR情報とGitHub上の状態の収集

以下を取得する。

- PR情報: repository名、タイトル、本文、base・head branch、最新head commit SHA
- 変更内容: 変更ファイル一覧、diff、コミットメッセージ
- CI: checkの結果、失敗したcheckの名前・URL・取得可能な関連ログ
- 自分の既存レビュー: 未resolve threadと会話、`APPROVED` / `CHANGES_REQUESTED` レビューID

最新head commit SHAは `<latest-commit-sha>` として保持する。
CIの失敗はレポートの概要に記載し、Finderの内部証拠として使用する。
自分の既存threadと会話はVerifierの反証材料として使用し、投稿前のthread IDを `<existing-thread-ids>`、レビューIDを `<existing-review-ids>` として保持する。

さらに、Contract review用のspec contractを次の順で解決する。

1. `--spec` が指定されていれば、そのIssueを `gh issue view` で取得し、本文のcontractセクション群 (Context〜Out of Scope、Decision Log) を使う
2. PR本文に `Closes #N` があれば `gh issue view N` で本文を取得し、contractセクション群を使う

Issueがcontractセクション群 (Context〜Out of Scope) を持たない普通のIssueの場合は、本文全体をcontract相当として扱う。明文に無い期待を検査しない原則は変わらないため、記述の薄いIssueではContract指摘は自然に少なくなる。

どちらでも解決できない場合はContract軸をスキップし、レポートの概要にその旨を1行記載する。解決したcontractは `<spec-contract>` として保持する。

他のレビュワーのレビューやthreadは参照しない。初回レビューではどちらのID一覧も空になる。

#### Phase 1.3: worktreeとレビュー環境の準備

1. `<repo-root>/.tmp/<repo-name>-worktrees/pr-<number>-review` を専用 worktree path とする。
2. 同じ path の worktree が存在し、未commit変更がある場合は中止する。clean な場合のみ作り直してよい。
3. PRの最新head commitとbase branchを取得し、head commitをdetached状態で専用worktreeにcheckoutする。
4. 専用worktreeをレビュー対象のsnapshotとし、Phase 2以降では対象ファイルをすべてこのsnapshot内から参照する。

### Phase 2: レビュー

#### Phase 2.1: FinderとStandardsとContract SubAgentの実行

`code-reviewer-finder` と `code-reviewer-standards` を並列に起動する。`<spec-contract>` を解決できた場合は `code-reviewer-contract` も並列に起動する。
Finderはmergeを止める問題の指摘候補を、Standardsはmergeをブロックすべき規約違反・コードスメルの指摘候補を、Contractはspec contractとの食い違い (未充足・boundary違反・scope creep) の指摘候補を収集する。specとコードのどちらが正しいかは判定せず、どちらかを直して一致させることを完了条件にする。
レビュー方法、実行制約、出力形式はそれぞれのagent定義に従う。
次のprompt templateを使用する。

```text
以下の対象変更を、agent定義の責務・判定基準・出力形式に従ってレビューする。
あなたの役割: <role>

対象変更:
- 対象種別: GitHub PR
- PR番号: <pr-number>
- 変更目的・説明: <pr-title-and-body>
- 変更ファイル一覧: <changed-files>
- diff: <diff>
- 変更履歴: <commits>
- 変更サマリ: <change-summary>
- snapshotの絶対パス: <snapshot-path>
- baseline識別子: <base-sha>
- snapshot識別子: <head-sha>
- 追加証拠: <ci-evidence>
- spec contract: <spec-contract>
```

`<role>` には `Finder`、`Standards`、`Contract` のいずれかを指定する。`<spec-contract>` にはContract起動時のみ解決済みspec contract全文を指定し、FinderとStandardsでは `なし` とする。
`<change-summary>` にはchangedFiles / additions / deletionsを、`<ci-evidence>` には失敗したCI結果のサマリとcheckの名前・URL・関連ログを指定する。
該当するCI結果がなければ `なし` とする。

#### Phase 2.2: 候補の選別と検証

各SubAgentの出力から候補を選別し、候補ごとに独立した `code-reviewer-verifier` を並列に起動して反証を試みる。verdictが `confirmed` の候補だけを確定指摘とし、`refuted` / `uncertain` は破棄する。候補が0件ならこのステップをスキップする。

- 各SubAgentが出力した指摘をすべて候補とする。verifierの起動前に、同じ `filepath:line` または同じ根本原因の候補を1件にまとめる。重複統合はこの1回だけとする
- Finder候補は、自分の既存未resolve threadと照合し、同じ根本原因の会話をverifierの反証材料にする
- Standards候補とContract候補は、先に確定した指摘と同じ行または同じ根本原因のものを破棄する (要修正事項を優先するため、Finder → Standards → Contract の順に確定する)

次のprompt templateを使用する。

```text
次のコードレビュー候補1件を、支持せずに反証を優先して独立検証する。
候補種別: <candidate-type>
検証対象の指摘:
<candidate>

対象変更:
- 対象種別: GitHub PR
- PR番号: <pr-number>
- 変更目的・説明: <pr-title-and-body>
- 変更ファイル一覧: <changed-files>
- diff: <diff>
- snapshotの絶対パス: <snapshot-path>
- baseline識別子: <base-sha>
- snapshot識別子: <head-sha>
- 追加証拠:
  - CI: <ci-evidence>
  - 同じ根本原因の既存thread: <related-thread>
  - spec contract: <spec-contract>
```

`<candidate>` には候補1件の全文を指定し、由来ごとに次の値を指定する。その他のplaceholderにはPhase 2.1と同じ値を指定する。

| 由来      | `<candidate-type>` | `<related-thread>`                              | `<spec-contract>`         |
| --------- | ------------------ | ----------------------------------------------- | ------------------------- |
| Finder    | `Finder`           | 同じ根本原因の既存threadと会話。無ければ `なし` | `なし`                    |
| Standards | `Standards`        | `なし`                                          | `なし`                    |
| Contract  | `Contract`         | `なし`                                          | 解決済みspec contract全文 |

確定指摘は、由来、`path` / `line` / `side`、`カテゴリ`、`要約`、`問題`、`完了条件`、SubAgentが出力した `証拠` (Finder) または `根拠` (Standards / Contract)、verifierの `根拠` と `実行結果` を内部レコードとして保持する。verifierの「完了条件の評価」を反映し、実装方法を指定せず、問題が解消されたと判断できる状態を `完了条件` に残す。

#### Phase 2.3: 確定指摘の校正とレポートの生成

1. PRのタイトルと本文から出力言語を決める。主に日本語の場合は `ja`、それ以外または判定が曖昧な場合は `en`
2. [確定指摘の書き方と findings.json](references/findings.md) に従い、確定指摘を校正して `findings.json` に書き出す。件数、順序、採否、技術的な意味、対象範囲、`path` / `line` / `side` は変えない
3. public repositoryへ投稿するとき、private (internalを含む) repositoryの情報を書かない。参照先の公開状態は書く前に確認し、確認できなければprivateとして扱う。伏せるときはrepository名、Issue/PR番号、URL、branch名、参照先固有のファイルパスや固有名詞を書かず、参照先で確認した事実だけを残す
4. レビュー実行ごとに `mktemp -d` で一意な `<review-temp-dir>` を作成し、`findings.json` をそこに置いてレポート本文とinline commentsを生成する。並び順、連番、項目名、Verdict、フッターはscriptが決める。検証エラーが出た場合は `findings.json` を直して再実行する

   ```bash
   python "<skill-dir>/scripts/render_review.py" \
     --findings "<review-temp-dir>/findings.json" \
     --out-dir "<review-temp-dir>"
   ```

   `<review-temp-dir>/body.md` と `<review-temp-dir>/comments.json` が生成され、標準出力にVerdict (`APPROVE` または `REQUEST_CHANGES`) が出力される。指摘が1件以上なら `REQUEST_CHANGES`、0件なら `APPROVE` になる。self reviewを含め、レポート内では `COMMENT` を使用しない。GitHub APIへ渡すeventはPhase 3.1で決める

確定指摘の内部レコードは校正後も保持する。

### Phase 3: レビューの投稿と置き換え

`--dry-run` が指定されていない場合のみ実行する。
最初にPRの現在のhead commit SHAを再取得し、Phase 1で保持した`<latest-commit-sha>`と比較する。一致しない場合は投稿、dismiss、resolveをすべてスキップしてPhase 4に進む。

#### Phase 3.1: event種別の決定

- self review モードでは `--event COMMENT` を渡すが、body 内の Verdict 表記は元のまま(`APPROVE` または `REQUEST_CHANGES`)にする(GitHub の仕様で自分の PR に `APPROVE` / `REQUEST_CHANGES` は投稿できないため)。
- self review 以外の通常レビューでは、Phase 2.3のVerdictをそのまま `--event` に渡す

#### Phase 3.2: レビューの投稿

Phase 2.3で生成した `body.md` と `comments.json` を `scripts/post_review.sh` に渡してGitHub API経由でレビューを投稿する。

```bash
bash "<skill-dir>/scripts/post_review.sh" \
  --repo "<owner/repo>" \
  --pr "<number>" \
  --commit "<latest-commit-sha>" \
  --event "<APPROVE|REQUEST_CHANGES|COMMENT>" \
  --body-file "<review-temp-dir>/body.md" \
  --comments-file "<review-temp-dir>/comments.json"
```

- 成功時は PR レビューの URL が標準出力に出力される
- レビュー本文とinline commentはファイルで渡す。`gh pr review --body ...`、`gh api -f body=...`、シェル上で組み立てたJSON文字列の直接渡しは、引用符やJSONのエスケープが崩れるため使わない
- diffに含まれない `(path, line, side)` のentryは `post_review.sh` がinline対象から除外して標準エラーに `Warning:` を出力する。レポート本文は変わらない

#### Phase 3.3: 以前のレビューの後始末

Phase 3.2の投稿が成功した後にのみ実行し、最新レビューだけを現在有効なレビューとして残す。投稿が失敗した場合は何もしない(古いレビューを残すことで「新規レビューなし」の空白状態を回避する)。初回レビュー時は対象0で自然にスキップされる。

**既存レビューのdismiss**

Phase 1.2 で取得した `<existing-review-ids>` (投稿前のsnapshot) を `--review-id` で渡す。

```bash
bash "<skill-dir>/scripts/dismiss_my_reviews.sh" \
  --repo "<owner/repo>" \
  --pr "<number>" \
  --review-id "<id1>" --review-id "<id2>"
```

`<existing-review-ids>` が空の場合は dismiss スクリプトを呼び出さない。

**以前のinline commentのresolve**

Phase 1.2 で取得した `<existing-thread-ids>` のthreadを、outdatedかどうかに関係なくすべてresolveする。最新headへの新しいレビューが投稿済みのため、以後は新しいレビューだけを対応対象とする。

```bash
bash "<skill-dir>/scripts/resolve_review_threads.sh" \
  --thread-id "<id1>" --thread-id "<id2>"
```

`<existing-thread-ids>` が空の場合はresolveスクリプトを呼び出さない。
スクリプトは指定されたthread IDだけをresolveする。

### Phase 4: 終了処理

レビュー用に作成したworktree、一時Git ref、投稿用の `<review-temp-dir>` を削除する。処理が中断した場合も同様に削除する。

開始時の`<latest-commit-sha>`に対するレビューとして、以下をまとめてユーザーに提示して終了する。

- Verdict、Finder由来・Standards由来・Contract由来の指摘件数 (Contract軸をスキップした場合はその旨)、レポート本文
- レビューURL(`post_review.sh` の標準出力)。`--dry-run`、head commit更新、投稿失敗のいずれかで未投稿の場合は、その理由を明記する
- dismissした既存レビューとresolveした以前のthreadの件数(Phase 3.3を実行した場合のみ)
