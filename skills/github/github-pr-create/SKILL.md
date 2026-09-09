---
name: github-pr-create
description: >-
  Pull Requestを作成するSkill。現在のbranchからpull requestを作成する。言語指定可能。
  ユーザーが「PR作って」「pull request作成して」のように依頼したら使うこと。
allowed-tools: Read, Write, Task, AskUserQuestion, Skill(git-commit), Bash(git:*), Bash(gh:*), Bash(cat:*), Bash(ls:*), Bash(bat:*), Bash(eza:*), Bash(grep:*), Bash(head:*), Bash(tail:*), Bash(mktemp:*)
---

# Create Pull Request

現在のbranchからpull requestを作成するSkill。PRのタイトルと説明文は、変更内容に基づいて自動生成する。PRの説明文は、コードを参照しなくてもPRの内容が理解できるように、概要・背景、関連Issue、実装方針、変更内容、影響範囲、検証結果を説明する。

## Arguments

引数は自由文でよい。次の項目を読み取る。

- `language`: PRのタイトルと説明文の言語 (例: "ja", "en")。明示が無い場合は、repositoryのPR templateの言語を使う。templateが無ければ会話の言語に従う
- `spec`: 解決するGitHub Issue番号 (任意。呼び出し元のskillから渡される)。関連Issue (`Closes`) の最優先候補として扱う
- `--dry-run`: 生成したPRタイトル・本文・base/head branchと、図・画像があればローカル成果物を提示する。push、添付のアップロード、`gh pr create` は実行せず終了する

base branchは引数ではなく「0. 事前チェック」の2で決定する。ユーザーが会話で明示した場合 (「developに向けてPRを作って」等) はそれを最優先する。

## 0. 事前チェック

1. **branchとcommitの準備**:
   - 現在のbranchがdefault branch (`main`, `master` 等) の場合、または未commitの変更がある場合は、branch名とcommitの分割案を提示して承認を得る。ここで中止すると、ユーザーは同じ変更を自分でcommitし直してから再度依頼することになるため
   - 承認後、branch作成とcommitはgit-commit skillへ委譲する
   - 承認が得られない場合はここで中止する
2. **base branchの決定**:
   - ユーザーが会話でbase branchを明示した場合は、それを最優先で使用する
   - 明示が無い場合は、repositoryのdefault branch (`gh repo view --json defaultBranchRef --jq '.defaultBranchRef.name'`) を使う
   - `git log --oneline origin/<base>..HEAD` に今回の作業と無関係なcommitが混ざっている場合のみ、baseを選び直す:
     1. open PRのhead branch (`gh pr list --json headRefName`) を候補に加える
     2. 各候補について `git merge-base HEAD origin/<候補>` からHEADまでのcommit数を数える
     3. commit数が最小の候補をbaseにする。1つに決まらなければ、AskUserQuestionで候補branchを提示してユーザーに確認する
   - 決定後、選定したbaseとその理由、`git log --oneline origin/<base>..HEAD` の一覧を必ず報告する (選定が誤っていればユーザーがここで気付ける)
   - tracking branch (`@{upstream}`) はpush先の判定にだけ使い、PRのbase branchとして扱わない。feature branchのupstreamは通常 `origin/<current-branch>` であり、baseに使うと `origin/<base>..HEAD` が空になるため
3. **既存PRの確認**:
   - `gh pr view --json url,state` で既存のPRを確認
   - PRが既に存在する場合は、そのURLと状態を表示して中止
4. **base branchの最新化**:
   - 比較基準を最新化するため、base branch決定後に `git fetch origin <base-branch>` を実行する
   - 以降のcommit確認と差分取得では、最新化した `origin/<base-branch>` を基準にする
5. **commitの存在確認**:
   - `git log origin/<base-branch>..HEAD` が空でないことを確認
   - commitがない場合は中止
6. **PR templateの確認**:
   - 以下のパスを順に確認し、最初に見つかったものを使用:
     - `.github/pull_request_template.md`
     - `.github/PULL_REQUEST_TEMPLATE.md`
     - `.github/PULL_REQUEST_TEMPLATE/` ディレクトリ内のファイル
     - `docs/pull_request_template.md`
   - repositoryにPR templateが存在しない場合、指定言語に応じて以下を使用:
     - English: [`references/pr_template.md`](references/pr_template.md)
     - Japanese: [`references/pr_template_ja.md`](references/pr_template_ja.md)
   - repositoryにtemplateがある場合は、その見出しと順序をそのまま使う。「4. 説明文の生成」の6項目に足りない見出しがあっても補わない。そのrepositoryのreviewerが何を読みたいかは、skillの既定よりrepositoryのtemplateのほうが正確に表すため
7. Conventional Commits規約 [`references/conventional_commits.md`](references/conventional_commits.md)

## 1. リモートへのpush

- `--dry-run` が指定された場合はpushを行わず、以降の差分取得はローカルのcommitと `origin/<base-branch>` の比較のみで行う
- `git push` または `git push -u origin <current-branch>` で現在のbranchをpushする
- 通常のpushが失敗し、履歴書き換えが必要な場合のみ、ユーザーに確認して `git push --force-with-lease` を実行する

## 2. 変更内容の取得

次の2つを**必ず**実行し、この出力を本文の根拠にする。同じ会話で実装した場合でも省略しない。記憶から書くと、途中で捨てた変更や別branchの作業が本文に混ざり、「4. 説明文の生成」末尾のdiffとの照合が空振りするため。

```bash
git log --oneline origin/<base-branch>..HEAD
git diff --stat origin/<base-branch>..HEAD
```

- statで変更行数が大きいファイルと、振る舞いが変わるファイルは `git diff origin/<base-branch>..HEAD -- <file>` で個別に確認する
- lockfileの更新やformatterの一括適用のような機械的な差分は、statだけで済ませてよい

## 3. PRタイトル、関連Issue、Labelの生成

「2. 変更内容の取得」で得た差分とcommitを根拠に、以下を順に決定する。

### タイトル

- Conventional Commits規約に従い、commitとブランチの差分の内容を要約した簡潔なタイトルにする
- 1つのcommitのみの場合、そのcommitメッセージをベースにする

### 関連Issue

- `spec` としてIssue番号が渡された場合は、それを解決するIssue (`Closes`) の最優先候補にする
- branch名からIssue番号を抽出する (例: `feature/123-add-something` → `#123`)
- commitメッセージから `fix #456`, `closes #789`, `refs #101` 等のキーワードを検出する
- `gh issue list --state open --json number,title` のタイトルを変更内容と突き合わせ、関連するIssueを探す
- 検出したIssueはタイトルだけで判断せず、本文を読んで問題、背景、受け入れ条件を確認する
- open issueが大量にある場合は、検索条件を絞るか、この突き合わせのみSubAgentに委譲してよい

### Label

- リポジトリのlabelを取得し、その中から選定する: `gh label list --json name,description`
- 存在しないlabelは付与しない。合うlabelが無い場合は付与しない

## 4. 説明文の生成

- **PR template**: 「0. 事前チェック」で選択したtemplateの見出し・順序・言語に従う (repositoryのtemplateは指定言語では翻訳しない)
- 「2. 変更内容の取得」で取得したcommit一覧と差分を根拠にして本文を生成する
- 使用するtemplateによって、以下の6項目の扱いを変える
  - skill同梱のtemplateを使う場合: 6項目を必ずこの順序で記載する。小さいPRでも項目を省略せず、内容を簡潔にする
  - repositoryのtemplateを使う場合: そのtemplateの見出しに対応する項目だけを、以下の説明に沿って書く
  1. **概要・背景 / Overview and Background**: 最初にこのPRで実現する結果を述べ、続けて変更前の挙動、発生条件、原因、利用者や運用への影響を説明する。同じ内容を概要と背景として繰り返さない
  2. **関連Issue / Related Issues**: 解決するIssueには `Closes #xxx`、参照のみのIssueには `Related to #xxx` を使う
  3. **実装方針 / Implementation Approach**: 解決方法を概念的に説明し、その方法を選んだ理由を記載する。非自明な設計判断がある場合は、制約や採用しなかった案の理由も記載する
  4. **変更内容 / Changes**: diffをファイル単位で言い換えるだけではなく、変わる挙動や責務ごとに主な変更をまとめる。formatterの一括適用やlockfile更新のような機械的な変更は、個別に列挙せず1つの箇条書きにまとめる
  5. **影響範囲 / Impact**: user-facing change、互換性、performance、security、deployment、既知の制約から該当するものを記載し、影響しない範囲も明確にする
  6. **検証結果 / Validation Results**: 何をどの方法で検証し、どの結果になったかを記載する。bug修正やperformance変更では、可能な限り変更前後を比較できる再現結果、log、数値を示す

- 該当する内容がない項目は、削除したり埋め草で埋めたりせず、指定言語で該当なし (英語は `N/A`) と明記する
- 箇条書きは1行1変更とし、指定言語に応じて以下の文体で書く
  - 日本語: 体言止めで終える。ですます調は使わない
    - GOOD: `- ログイン失敗時のリトライ処理を追加`
    - BAD: `- ログイン失敗時のリトライ処理を追加しました`
  - 英語: Conventional Commitsのdescriptionと同じ命令形の断片で書く (例: `- Add retry on login failure`)
- 検証で実行したコマンドと結果は、コピペ可能な形式で記載する
- CIで自動実行されるlint・format・型チェックは記載しない (そのチェック設定自体を変更したPRを除く)。記載するのはCIが検証しない動作確認の手順と結果
- テストを実行していない場合は、未実行であることと理由を明記する
- diff、commit、関連Issueから確認できない事実を推測で補わない。本文の理解に必要な情報が不足する場合はユーザーに確認する
- PR作成前に、使用したtemplateの見出しがすべて埋まり、templateの説明コメントや未記入のplaceholderが残っていないことを確認する
- PR作成前に、変更内容の各箇条書きをdiffと照合し、diffに無い変更と文体規則違反 (日本語のですます調など) が残っていないことを確認する

### 表現の選択

単純な手順は番号付きリスト、短い比較や測定値はMarkdown表、小さなコード・構造の変更は `diff` コードブロックにする。関係や差異が文章だけでは掴みにくい場合は、[図と画像の規則](references/visuals.md) を読んでMermaid・SVG・PNGを選ぶ。図専用の必須セクションは増やさず、実装方針・変更内容・検証結果など既存の対応するセクションへ置く。

- UI変更は同じ画面・操作条件のbefore/after、処理変更は分岐や通信順序、責務の移動は変更前後の構成を示す
- 性能のグラフは実測データから生成し、測定条件と値を併記する。未実行の測定結果は補わない
- 図のノード・矢印・数値もdiffや検証結果と照合する。概念図は実装の説明、スクリーンショットは実際の表示結果として区別する
- 画像は一意な一時ディレクトリに用意し、ローカルで表示確認する。画像の生成・表示手段が無い場合は、未確認の画像を添付せず不足を報告する

## 5. Pull Requestの作成

`--dry-run` が指定された場合は、生成したPRタイトル・本文・base/head branchと、図・画像があればローカル成果物と本文内の配置を提示する。添付はアップロードせず、`gh pr create` を実行せずに終了する。

1. 生成したPR説明文は、先にMarkdownファイルへ書き出す:
   - 例: `/tmp/YYYYMMDD-HHMMSS-pr-body.md`
   - 本文は `--body-file` で渡す。複数行本文、Markdown、引用符、バッククォート、絵文字を `--body "<PR Description>"` のようにコマンド引数へ直接埋め込むとエスケープが崩れるため
2. PRを作成する:
   `--assignee @me` を**必ず**付与し、PRの担当者を自分 (PR作成者) に設定する
   画像があれば [添付手順](references/visuals.md#添付と確認) に従い、同じコマンドに画像ごとの `--attach` を付ける。

   ```bash
   gh pr create \
     --base <base-branch> \
     --title "<PR Title>" \
     --body-file /tmp/YYYYMMDD-HHMMSS-pr-body.md \
     --assignee @me \
     [--label <name> ...] \
     [--attach <image> ...]
   ```

   labelは「3. PRタイトル、関連Issue、Labelの生成」で決定した自動判定の結果を付与する (該当labelが無い場合は付与しない)

3. 作成されたPRを `gh pr view <url> --json body,url` で再取得し、本文と照合する。画像参照がアップロード先URLへ置換され、Mermaidブロックが保持されていることも確認する。投稿結果が不明な場合は同じPRを再作成せず、対象の作成状況を確認してから報告する。

## 6. 結果の表示

以下の情報をまとめて表示する:

- 作成したPRのURL
- タイトル
- base branch → head branch (baseを推定で決めた場合はその理由)
- 関連Issue (検出された場合)
- assignee (`@me`)
- label (自動付与された場合)
- 変更の概要 (ファイル数、追加行数、削除行数)
