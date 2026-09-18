---
name: github-pr-create
description: >-
  Pull Requestを作成するSkill。現在のbranchからpull requestを作成する。言語指定可能。
  ユーザーが「PR作って」「pull request作成して」のように依頼したら使うこと。
allowed-tools: Read, Write, Task, AskUserQuestion, Skill(git-commit), Bash(git:*), Bash(gh:*), Bash(cat:*), Bash(ls:*), Bash(bat:*), Bash(eza:*), Bash(grep:*), Bash(head:*), Bash(tail:*), Bash(mktemp:*)
---

# Create Pull Request

現在のbranchからpull requestを作成するSkill。PRのタイトルと説明文は、変更内容に基づいて自動生成する。

## Arguments

- `language`: PRのタイトルと説明文の言語 (例: "ja", "en")。明示が無い場合は、repositoryのPR templateの言語を使う。templateが無ければ会話の言語に従う
- `spec`: 解決するGitHub Issue番号 (任意。呼び出し元のskillから渡される)。関連Issue (`Closes`) の最優先候補として扱う
- `--dry-run`: 生成したPRタイトル・本文・base/head branchと、図・画像があればローカル成果物と本文内の配置を提示する。push、添付のアップロード、`gh pr create` は実行しない

## 0. 事前チェック

1. **branchとcommitの準備**: 現在のbranchがdefault branchの場合、または未commitの変更がある場合は、branch名とcommitの分割案を提示して承認を得てから、branch作成とcommitをgit-commit skillへ委譲する。ここで中止すると、ユーザーは同じ変更を自分でcommitし直してから再度依頼することになるため
2. **base branchの決定**:
   - ユーザーが会話で明示したbase branchを使う。明示が無ければrepositoryのdefault branchを使う
   - `git log --oneline origin/<base>..HEAD` に今回の作業と無関係なcommitが混ざる場合は、open PRのhead branchのうちHEADが直接積み上がっているものをbaseにする。1つに決まらなければ、AskUserQuestionで候補branchを提示してユーザーに確認する
   - 決定後、選定したbaseとその理由、`git log --oneline origin/<base>..HEAD` の一覧を報告する (選定が誤っていればユーザーがここで気付ける)
   - tracking branch (`@{upstream}`) はpush先の判定にだけ使い、PRのbase branchとして扱わない。feature branchのupstreamは通常 `origin/<current-branch>` であり、baseに使うと `origin/<base>..HEAD` が空になるため
3. **既存PRの確認**: 現在のbranchのPRが既に存在する場合は、そのURLと状態を表示して中止する
4. **base branchの最新化**: `git fetch origin <base-branch>` で比較基準を最新化し、以降のcommit確認と差分取得は `origin/<base-branch>` を基準にする
5. **PR templateの確認**: repositoryにGitHubが認識する場所のPR templateがあればそれを使い、見出しと順序をそのまま使う。同梱templateにある見出しが足りなくても補わない。そのrepositoryのreviewerが何を読みたいかは、skillの既定よりrepositoryのtemplateのほうが正確に表すため。無ければ指定言語に応じて同梱のtemplateを使う:
   - English: [`references/pr_template.md`](references/pr_template.md)
   - Japanese: [`references/pr_template_ja.md`](references/pr_template_ja.md)

## 1. リモートへのpush

現在のbranchをpushする。通常のpushが失敗し、履歴書き換えが必要な場合のみ、ユーザーに確認して `--force-with-lease` を使う。`--dry-run` ではpushせず、以降の差分取得はローカルのcommitと `origin/<base-branch>` の比較で行う。

## 2. 変更内容の取得

`origin/<base-branch>..HEAD` のcommit一覧とdiffを取得し、この出力を本文の根拠にする。同じ会話で実装した場合でも省略しない。記憶から書くと、途中で捨てた変更や別branchの作業が本文に混ざり、投稿前のdiffとの照合が空振りするため。lockfileの更新やformatterの一括適用のような機械的な差分は、statだけで済ませてよい。

## 3. PRタイトル、関連Issue、Labelの生成

「2. 変更内容の取得」で得た差分とcommitを根拠に、以下を決定する。

- **タイトル**: Conventional Commitsに従い、差分の内容を要約した簡潔なタイトルにする。1つのcommitのみの場合、そのcommitメッセージをベースにする
- **関連Issue**: `spec` で渡されたIssue番号を解決するIssue (`Closes`) の最優先候補にする。次にbranch名、commitメッセージ、open issueの一覧から関連するIssueを探し、タイトルだけで判断せず本文を読んで問題、背景、受け入れ条件を確認する。open issueが大量にある場合は、この突き合わせをSubAgentに委譲してよい
- **Label**: repositoryの既存labelから合うものを選ぶ。合うものが無ければ付与しない

## 4. 説明文の生成

- **PR template**: 「0. 事前チェック」で選択したtemplateの見出し・順序・言語に従う (repositoryのtemplateは指定言語では翻訳しない)。各見出しの書き方は同梱templateのコメントに従う。repositoryのtemplateでも、意図が同じ見出しには同じ書き方を当てる。小さいPRでも見出しを省略せず、内容を簡潔にする
- 該当する内容がない項目は、削除したり埋め草で埋めたりせず、指定言語で該当なし (英語は `N/A`) と明記する
- 箇条書きは1行1変更とし、指定言語に応じて以下の文体で書く
  - 日本語: 体言止めで終える。ですます調は使わない
    - GOOD: `- ログイン失敗時のリトライ処理を追加`
    - BAD: `- ログイン失敗時のリトライ処理を追加しました`
  - 英語: Conventional Commitsのdescriptionと同じ命令形の断片で書く (例: `- Add retry on login failure`)
- 検証で実行したコマンドと結果は、コピペ可能な形式で記載する
- CIで自動実行されるlint・format・型チェックは記載しない (そのチェック設定自体を変更したPRを除く)。記載するのはCIが検証しない動作確認の手順と結果
- diff、commit、関連Issueから確認できない事実を推測で補わない。本文の理解に必要な情報が不足する場合はユーザーに確認する
- public repositoryへ投稿するとき、private (internalを含む) repositoryの情報を書かない。参照先の公開状態は書く前に確認し、確認できなければprivateとして扱う。伏せるときはrepository名、Issue/PR番号、URL、branch名、参照先固有のファイルパスや固有名詞を書かず、参照先で確認した事実だけを残す
- 投稿前に本文を見直す: templateの見出しがすべて埋まりコメントやplaceholderが残っていないこと、各箇条書きがdiffにあり文体規則に沿うこと、private repositoryの情報が残っていないこと

### 表現の選択

単純な手順は番号付きリスト、短い比較や測定値はMarkdown表、小さなコード・構造の変更は `diff` コードブロックにする。関係や差異が文章だけでは掴みにくい場合は、[図と画像の規則](references/visuals.md) を読んでMermaid・SVG・PNGを選ぶ。図専用の必須セクションは増やさず、実装方針・変更内容・検証結果など既存の対応するセクションへ置く。

## 5. Pull Requestの作成

本文はMarkdownファイルへ書き出し、`--body-file` で渡す。複数行本文、引用符、バッククォート、絵文字を `--body` の引数へ直接埋め込むとエスケープが崩れるため。
`--base <base-branch>`、`--assignee @me`、決定したlabel、画像があれば画像ごとの `--attach` を付けて `gh pr create` を実行する。添付があれば [添付手順](references/visuals.md#添付と確認) の投稿後確認を行う。

## 6. 結果の表示

以下の情報をまとめて表示する:

- 作成したPRのURL
- タイトル
- base branch → head branch (baseを推定で決めた場合はその理由)
- 関連Issue (検出された場合)
- assignee (`@me`)
- label (自動付与された場合)
- 変更の概要 (ファイル数、追加行数、削除行数)
