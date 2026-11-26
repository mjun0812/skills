---
name: github-pr-review
description: >-
  GitHubのPull Requestを敵対的にコードレビューし、検証を通過した指摘だけをレビューレポートとinline commentで投稿するSkill。self reviewにも対応する。
  ユーザーが「このPRをレビューして」のように依頼したら使うこと。
allowed-tools: Task, Read, Write, AskUserQuestion, Bash(git:*), Bash(gh:*), Bash(jq:*), Bash(mkdir:*), Bash(mktemp:*), Bash(rm:*), Bash(bash:*), Bash(python:*)
---

# Pull Request Review

PRのhead commitをworktreeにチェックアウトし、重点の異なる2つのFinder SubAgentが指摘候補を探す。
Claim SubAgentは、PR本文が述べる検証の結果、範囲、影響範囲を実コードで確かめ、説明と実際の結果との食い違いを第2の軸として探す。
指摘候補は、1件ずつVerifier SubAgentが実コードを実行して反証を試みる。
再現できた指摘を要修正事項として、再現はできないが反証も無い指摘を未証明の指摘として、レビューレポートとinline commentに投稿する。

## Arguments

- `PR number`: レビューするPR番号 (optional, defaults to PR for current branch)
- `--auto`: Phase 2.4の投稿前の確認を省き、生成したレビューをそのまま投稿する

## Task

1回の実行で扱うPRは1件だけとする。複数のPRのレビューを依頼された場合は、同じcontextで並行させず、1件のPhase 4が終わってから次のPRを始める。並行させると、別のPRのdiffや本文を入力として渡してしまう。

### Phase 1: 準備

#### Phase 1.1: 対象PRの特定

- **引数にPR番号が指定されている場合**: 指定されたPRを対象にする
- **引数なし**
  - **現在のブランチに紐づくopen PRが存在する場合**: そのPRをそのまま使用する(確認なし)
  - **現在のブランチに紐づくopen PRが存在しない場合**: RemoteのOpen PR一覧を取得し、`AskUserQuestion`でユーザーに対象PRを確認する。Open PRが1件もなければその旨を報告して終了する

#### Phase 1.2: PR情報とGitHub上の状態の収集

以下を取得する。

- PR情報: repository名、タイトル、本文、base・head branch、最新head commit SHA
- CI: checkの結果、失敗したcheckの名前・URL・取得可能な関連ログ
- 自分の既存レビュー: 以前に投稿した指摘と返信、`APPROVED` / `CHANGES_REQUESTED` レビューID

最新head commit SHAは `<latest-commit-sha>` として保持する。
CIの失敗はレポートの概要に記載し、Finderの内部証拠として使用する。
以前に投稿した指摘は、resolve済みのthreadも含めて返信とともに取得する。返信には、各指摘を修正したか、見送ったか、却下したかが記録されている。再レビューのたびに以前のthreadはresolveされるため (Phase 3.3)、未resolveのthreadだけを見ると前々回以前の判断が抜け落ち、決着済みの指摘を蒸し返すことになる。

```bash
bash "<skill-dir>/scripts/fetch_prior_findings.sh" --repo "<owner/repo>" --pr "<number>"
```

出力はPhase 1.3で `<review-temp-dir>/prior-findings.json` に書き出す。このうち `is_resolved` がfalseのthread IDを `<existing-thread-ids>`、レビューIDを `<existing-review-ids>` として保持する。

他のレビュワーのレビューやthreadは参照しない。初回レビューではどちらのID一覧も空になる。

#### Phase 1.3: worktreeとレビュー環境の準備

1. `<repo-root>/.tmp/<repo-name>-worktrees/pr-<number>-review` を専用worktree pathとする。
2. 同じpathのworktreeが存在し、未commit変更がある場合は中止する。cleanな場合のみ作り直してよい。
3. PRの最新head commitとbase branchを取得し、head commitをdetached状態で専用worktreeにcheckoutする。
4. 専用worktreeをレビュー対象のsnapshotとし、Phase 2以降では対象ファイルをすべてこのsnapshot内から参照する。
5. レビュー実行ごとに `mktemp -d` で一意な `<review-temp-dir>` を作成する。SubAgentへの大きな入力は、promptに埋め込まずこのdirectoryのファイルで渡す。
6. レビュー範囲を決め、diff、変更ファイル一覧、変更履歴を `<review-temp-dir>` に書き出す。

   ```bash
   bash "<skill-dir>/scripts/resolve_review_range.sh" \
     --repo "<owner/repo>" --pr "<number>" \
     --base-ref "<fetched-base-ref>" --head "<latest-commit-sha>" \
     --out-dir "<review-temp-dir>"
   ```

   標準出力のJSONの `baseline` を `<baseline-sha>` として保持する。baselineはbase branchとのmerge-baseで、base branchに後から入った変更をdiffに含めない。PRのcommitに未mergeの別のopen PRのheadが含まれる積み上げPRでは、そのheadがbaselineになる。このとき `dependencyPr` のPRの変更はレビュー対象外とし、その旨を `<pr-title-and-body>` の末尾に1行追記してSubAgentへ伝える。

7. Phase 1.2で取得した以前の指摘を `<review-temp-dir>/prior-findings.json` に書き出す。

### Phase 2: レビュー

#### Phase 2.1: FinderとClaim SubAgentの実行

最初に、変更の意図を自分の言葉で言い直す。PRのタイトルと本文、`commits.txt`、`diff.patch`から、このPRが実現しようとしていることと、変えないと述べていることを2〜3文にまとめ、`<intent>`とする。指摘は、この意図が破られるかどうかで判定される。

`code-reviewer-finder` を2つと、`code-reviewer-claim` を1つ、並列に起動する。
Finderはmergeを止める問題の指摘候補を、ClaimはPR本文の主張と実際の結果との食い違いの指摘候補を収集する。Claimは、説明とコードのどちらが正しいかは判定せず、どちらかを直して一致させることを完了条件にする。
FinderとClaimには、テストや再現コードの実行を許可する。実行は各SubAgentがsnapshotから書き出した実行用コピーで行わせ、snapshotのファイルは変更させない。
レビュー方法、実行の規則、出力形式はそれぞれのagent定義に従う。
次のprompt templateを使用する。

```text
以下の対象変更を、agent定義の責務・判定基準・出力形式に従ってレビューする。
あなたの役割: <role>
重点視点: <focus>

重点視点に限定せず、対象変更の全変更単位を確認する。

対象変更:
- 対象種別: GitHub PR
- PR番号: <pr-number>
- 変更目的・説明: <pr-title-and-body>
- 変更の意図: <intent>
- 変更ファイル一覧: <review-temp-dir>/changed-files.txt
- diff: <review-temp-dir>/diff.patch
- 変更履歴: <review-temp-dir>/commits.txt
- 変更サマリ: <change-summary>
- snapshotの絶対パス: <snapshot-path>
- baseline識別子: <baseline-sha>
- snapshot識別子: <head-sha>
- 追加証拠: <ci-evidence>
- 以前の指摘と対応: <review-temp-dir>/prior-findings.json

ファイルで渡した入力は、レビューを始める前に全文を読む。
```

`<role>` と `<focus>` は次の組み合わせを使用する。

- Finder 1: `Finder` / 期待される振る舞い、契約、不変条件、呼び出し経路、状態・データの流れ、同時に更新すべきdiff外の箇所
- Finder 2: `Finder` / 境界値、失敗、並行実行、互換性、信頼できない入力、回復不能な状態
- Claim: `Claim` / PR本文が述べる検証の結果、範囲、影響範囲と、実際の変更との食い違い

`<change-summary>` には `<review-temp-dir>/diff.patch` の変更ファイル数・追加行数・削除行数を、`<ci-evidence>` には失敗したCI結果のサマリとcheckの名前・URL・関連ログを指定する。
該当するCI結果がなければ `なし` とする。

起動したSubAgent (専用agentを使えない環境では、同じpromptを渡した汎用SubAgent) のいずれかが、同時実行数の上限などで起動できない、または結果を返さない場合は、diffを自分で読んで代わりにレビューしない。投稿、dismiss、resolveをせずにPhase 4へ進み、レビューできなかったことと原因を報告する。Phase 2.2のverifierも同じとする。

#### Phase 2.2: 候補の選別と検証

各SubAgentの出力から候補を選別し、候補ごとに独立した `code-reviewer-verifier` を並列に起動して反証を試みる。verdictが `confirmed` の候補だけを確定指摘とし、`refuted` / `uncertain` は破棄して、verdictごとの件数を数える。確定指摘は、verifierの `証明` で2つに分ける。`再現` の指摘は要修正事項とし、`追跡` の指摘は未証明の指摘とする。候補が0件ならこのステップをスキップする。

- 各SubAgentが出力した指摘をすべて候補とする。verifierの起動前に、同じ `filepath:line` または同じ根本原因の候補を1件にまとめる。重複統合はこの1回だけとする
- 候補を `prior-findings.json` の以前の指摘と照合する。同じ根本原因の以前の指摘が見送りか却下で決着している候補は、その判断の前提が対象変更で崩れたことを候補自身が `file:line` で示していない限り、verifierの前で破棄する。修正済みとされた指摘と同じ根本原因の候補は、修正が不十分だという主張としてverifierへ渡す。照合した以前の指摘と返信は `<related-thread>` としてverifierの反証材料にする
- Claim候補は、先に確定したFinder由来の指摘と同じ行または同じ根本原因のものを破棄する。Finder、Claimの順に確定する
- Claimの出力の `一致` と `未確認` は候補にせず、主張の件数としてPhase 4の報告に使う

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
- 変更ファイル一覧: <review-temp-dir>/changed-files.txt
- diff: <review-temp-dir>/diff.patch
- snapshotの絶対パス: <snapshot-path>
- baseline識別子: <baseline-sha>
- snapshot識別子: <head-sha>
- 追加証拠:
  - CI: <ci-evidence>
  - 同じ根本原因の以前の指摘と返信: <related-thread>

ファイルで渡した入力は、検証を始める前に全文を読む。
```

`<candidate>` には候補1件の全文を、`<candidate-type>` には由来に応じて `Finder` か `Claim` を、`<related-thread>` には同じ根本原因の以前の指摘と返信を指定し、無ければ `なし` とする。その他のplaceholderにはPhase 2.1と同じ値を指定する。

確定指摘は、由来、`path` / `line` / `side`、`カテゴリ`、`要約`、`問題`、`完了条件`、SubAgentが出力したFinderの `証拠` またはClaimの `根拠`、verifierの `証明`、`根拠`、`実行結果` を内部レコードとして保持する。verifierの「完了条件の評価」を反映し、実装方法を指定せず、問題が解消されたと判断できる状態を `完了条件` に残す。

#### Phase 2.3: 確定指摘の校正とレポートの生成

1. PRのタイトルと本文を `<review-temp-dir>/pr.md` に書き出す
2. 出力言語をscriptで決める。標準出力の `ja` または `en` を、ユーザーとの会話言語やグローバル指示に関係なく使う

   ```bash
   python "<skill-dir>/scripts/render_review.py" --pr-text "<review-temp-dir>/pr.md"
   ```

3. [確定指摘の書き方と findings.json](references/findings.md) に従い、確定指摘を出力言語で校正して `<review-temp-dir>/findings.json` に書き出す。件数、順序、採否、技術的な意味、対象範囲、`path` / `line` / `side` は変えない
4. public repositoryへ投稿するとき、private (internalを含む) repositoryの情報を書かない。参照先の公開状態は書く前に確認し、確認できなければprivateとして扱う。伏せるときはrepository名、Issue/PR番号、URL、branch名、参照先固有のファイルパスや固有名詞を書かず、参照先で確認した事実だけを残す
5. レポート本文とinline commentsを生成する。並び順、連番、項目名、Verdict、フッターはscriptが決める。検証エラーが出た場合は `findings.json` を直して再実行する

   ```bash
   python "<skill-dir>/scripts/render_review.py" \
     --pr-text "<review-temp-dir>/pr.md" \
     --findings "<review-temp-dir>/findings.json" \
     --out-dir "<review-temp-dir>"
   ```

   `<review-temp-dir>/body.md` と `<review-temp-dir>/comments.json` が生成され、標準出力にVerdictとして `APPROVE` または `REQUEST_CHANGES` が出力される。要修正事項が1件以上なら `REQUEST_CHANGES`、0件なら `APPROVE` になる。未証明の指摘は、レポートとinline commentに載るが、Verdictを変えない。self reviewを含め、レポート内では `COMMENT` を使用しない。GitHub APIへ渡すeventはPhase 3.1で決める

確定指摘の内部レコードは校正後も保持する。

#### Phase 2.4: 投稿前の確認

`--auto` が指定されていない場合のみ実行する。

次をチャットに提示し、`AskUserQuestion` で「投稿する / 修正して再提示 / キャンセル」を確認する。承認されるまでPhase 3へ進まない。

- Verdictと、Phase 3.1で決まるGitHub APIのevent
- `<review-temp-dir>/body.md` の全文
- `<review-temp-dir>/comments.json` の各inline commentの `path:line` と本文
- 投稿後にdismissする既存レビューとresolveする以前のthreadの件数

「修正して再提示」の場合は、指示を `findings.json` に反映してPhase 2.3の手順5から再実行し、再び確認する。「キャンセル」の場合はPhase 3を実行せずPhase 4へ進む。

### Phase 3: レビューの投稿と置き換え

`--auto` が指定されているか、Phase 2.4で投稿が承認された場合のみ実行する。
最初にPRの現在のhead commit SHAを再取得し、Phase 1で保持した`<latest-commit-sha>`と比較する。一致しない場合は次のとおりにしてPhase 4に進む。

- 要修正事項か未証明の指摘が1件以上: Phase 3.2の手順で `<latest-commit-sha>` に対して `--event COMMENT` で投稿する。古いcommitに対するVerdictで現在のPRを承認・差し戻ししないためにCOMMENTを使い、確定した指摘はPR上に残す。Phase 3.3は実行しない
- 確定指摘が0件: 投稿、dismiss、resolveをすべてスキップする

#### Phase 3.1: event種別の決定

- self reviewモードでは `--event COMMENT` を渡すが、body内のVerdict表記は元のまま(`APPROVE` または `REQUEST_CHANGES`)にする(GitHubの仕様で自分のPRに `APPROVE` / `REQUEST_CHANGES` は投稿できないため)。
- self review以外の通常レビューでは、Phase 2.3のVerdictをそのまま `--event` に渡す
- head commitが進んでいた場合は、self reviewかどうかに関係なく `--event COMMENT` を渡す

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

- 成功時はPRレビューのURLが標準出力に出力される
- レビュー本文とinline commentはファイルで渡す。`gh pr review --body ...`、`gh api -f body=...`、シェル上で組み立てたJSON文字列の直接渡しは、引用符やJSONのエスケープが崩れるため使わない
- diffに含まれない `(path, line, side)` のentryは `post_review.sh` がinline対象から除外して標準エラーに `Warning:` を出力する。レポート本文は変わらない

#### Phase 3.3: 以前のレビューの後始末

Phase 3.2の投稿が成功した後にのみ実行し、最新レビューだけを現在有効なレビューとして残す。投稿が失敗した場合は何もしない(古いレビューを残すことで「新規レビューなし」の空白状態を回避する)。初回レビュー時は対象0で自然にスキップされる。

**既存レビューのdismiss**

Phase 1.2で取得した `<existing-review-ids>` (投稿前のsnapshot) を `--review-id` で渡す。

```bash
bash "<skill-dir>/scripts/dismiss_my_reviews.sh" \
  --repo "<owner/repo>" \
  --pr "<number>" \
  --review-id "<id1>" --review-id "<id2>"
```

`<existing-review-ids>` が空の場合はdismissスクリプトを呼び出さない。

**以前のinline commentのresolve**

Phase 1.2で取得した `<existing-thread-ids>` のthreadを、outdatedかどうかに関係なくすべてresolveする。最新headへの新しいレビューが投稿済みのため、以後は新しいレビューだけを対応対象とする。

```bash
bash "<skill-dir>/scripts/resolve_review_threads.sh" \
  --thread-id "<id1>" --thread-id "<id2>"
```

`<existing-thread-ids>` が空の場合はresolveスクリプトを呼び出さない。
スクリプトは指定されたthread IDだけをresolveする。

### Phase 4: 終了処理

レビュー用に作成したworktree、一時Git ref、`<review-temp-dir>` を削除する。処理が中断した場合も同様に削除する。

開始時の`<latest-commit-sha>`に対するレビューとして、以下をまとめてユーザーに提示して終了する。

- Verdict、言い直した変更の意図、要修正事項と未証明の指摘の件数とその由来の内訳、PR本文の主張のうち実行して一致した件数と実行できなかった件数、verifierが `refuted` と `uncertain` で破棄した候補のそれぞれの件数、以前の判断と同じ根本原因として破棄した候補の件数、レポート本文
- レビューURL(`post_review.sh` の標準出力)。head commitの更新によりCOMMENTで投稿した場合はその旨を書く。Phase 2.4でのキャンセル、SubAgentの起動失敗、指摘0件でのhead commit更新、投稿失敗のいずれかで未投稿の場合は、その理由を明記する
- dismissした既存レビューとresolveした以前のthreadの件数(Phase 3.3を実行した場合のみ)
