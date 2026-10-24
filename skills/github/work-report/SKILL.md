---
name: work-report
description: >-
  指定した期間 (日・週・月・四半期、既定は週) に、ユーザーがGitHubのowner (orgまたはuser) 配下で行ったPR・Issue・レビューの作業と、Claude Code・Codexとの会話で行った作業を集計し、repoとテーマごとに整理した1枚のHTMLの作業報告にするSkill。
  ユーザーが「今週の作業を報告書にして」「先月の作業をまとめて」「日報を作って」「四半期の振り返りを作って」のように依頼したら使うこと。
  1つのPRやIssueの説明、commit履歴の要約、チーム全体の統計には使わない。
allowed-tools: Read, Write, Bash(gh:*), Bash(python3:*), Bash(jq:*), Bash(mktemp:*)
---

# Work Report

指定した期間にユーザーが行った作業を、1枚のHTMLにまとめる。
材料はGitHubのPR・Issue・レビューと、Claude Code・Codexのsessionログの2つである。
集計と描画はscriptが行い、agentはitemの分類と各行の文言だけを決める。
ページの構成と見た目は`scripts/render_report.py`が固定するため、HTMLを手書きしない。

## 引数

| 引数         | 既定値                                                                                                   |
| ------------ | -------------------------------------------------------------------------------------------------------- |
| owner        | 必須。依頼かcwdのgit remoteから一意に分かればそれを使う。分からなければユーザーに確認する                |
| user         | ghで認証中のユーザー                                                                                     |
| 期間         | 週次 (今日を含む直近7日間)。言い方と期間の対応は次の表に従う                                             |
| タイムゾーン | 実行環境のローカル。ユーザーが指定したとき、または夏時間のある地域では、IANA名 (例: `Asia/Tokyo`) で渡す |
| 対象名       | ページのタイトルに使う名前。既定はowner名。ユーザーがプロジェクト名で呼んでいればその名前を使う          |
| 前回の報告   | 任意。URLかファイル。渡されたら重複の除外に使う                                                          |

| 依頼の言い方                  | 種類         | 期間                                                                                           |
| ----------------------------- | ------------ | ---------------------------------------------------------------------------------------------- |
| 指定なし                      | 週次         | 今日を含む直近7日間                                                                            |
| 今日、昨日、日付1つ           | 日次         | その日                                                                                         |
| 今週、先週                    | 週次         | 月曜から日曜まで。今週は今日まで                                                               |
| 今月、先月、`YYYY-MM`         | 月次         | 1日から末日まで。今月は今日まで                                                                |
| 今四半期、前四半期、`YYYY Qn` | 四半期       | 暦年の四半期 (1〜3月がQ1)。今四半期は今日まで                                                  |
| 開始日と終了日                | 日数で決める | 指定どおり。1日なら日次、7日なら週次、暦月なら月次、暦年の四半期なら四半期、それ以外は任意期間 |

週の始まりや年度の区切りをユーザーが指定したら、それに従う。
日付は`python3`で計算し、暗算しない。`date`の引数はmacOSとLinuxで異なるため使わない。

## 手順

### 1. GitHubの作業を集計する

```bash
work_dir="$(mktemp -d)"
python3 "<skill-dir>/scripts/collect_activity.py" \
  --owner "<owner>" --since "<YYYY-MM-DD>" --until "<YYYY-MM-DD>" \
  [--user "<login>"] [--tz "<IANA名>"] > "$work_dir/activity.json"
```

`<skill-dir>`はこのSKILL.mdがあるディレクトリを指す。scriptはPython 3.11以上の標準libraryで動く。出力のJSONは次のとおり。

- `items`: 期間内にuserの操作があるPR・Issueと、userへのレビュー依頼が残っているopen PR。`actions`は期間内のuserの操作 (timelineのevent名と時刻)、`review_pending`はレビュー待ちかどうかを表す
- `excluded`: userが関与している (作成者・担当・言及・コメント・レビュー) が、期間内に操作がないitem
- `queries`: 使った検索条件
- `warnings`: 検索APIの上限の1,000件を超えて読み切れなかった検索。closeの検索なら期間を分けて実行し直し、結果を合わせる。それ以外の検索なら、読み切れなかったことをfooterと報告に書く

時刻はすべて指定したタイムゾーンへ換算済みである。日付はこの値から取り、自分でタイムゾーンを換算しない。
`state`は期間の終了時点の状態、`current_state`は実行した時点の状態を表す。`review_pending`も実行した時点の状態である。

### 2. 会話ログを集計する

```bash
python3 "<skill-dir>/scripts/collect_sessions.py" \
  --since "<YYYY-MM-DD>" --until "<YYYY-MM-DD>" [--tz "<IANA名>"] > "$work_dir/sessions.json"
```

期間内にユーザーが発話したClaude CodeとCodexのsessionが、開始の早い順に`sessions`へ入る。subagentのthreadと、非対話で起動したCodexは含まない。

- `agent`: `claude-code`か`codex`
- `repo`: 作業ディレクトリのGitHub上のrepo (`owner/name`)。repoの外なら`null`
- `title`: agentが付けたsessionの題名
- `prompts`と`prompt_count`: 期間内のユーザーの発話のうち最初の3件 (先頭300文字) と、発話の件数
- `last_reply`: 期間内のagentの最後の返答 (先頭500文字)
- `github_refs`: agentの返答に出てきたPR・IssueのURL
- `path`: sessionログのファイル。ここまでの情報で何をしたか分からないsessionだけ、必要な部分を読む
- `warnings`: agentの返答はあるのにユーザーの発話を読み取れなかったログ。ログの形式の変更が考えられるので、報告で伝える

sessionが多いとき (月次や四半期) は、先に`jq`で`agent`・`repo`・`title`・`started_at`・`prompt_count`だけの一覧を作り、行のまとめ方を決めてから、必要なsessionの詳細を読む。

### 3. 前回の報告との重複を除く

前回の報告が渡された場合だけ行う。
前回すでに載っているmerge・close・起票のitemは今回から除き、footerに除いたことを書く。
前回から続くレビュー待ちは今回も載せる。

### 4. 分類して文言を書く

`references/report.md`の形式で`$work_dir/report.json`を書く。
ページの言語は会話の言語に合わせ、`lang`に設定する。この節の見出しやラベルの例は日本語の場合の書き方で、他の言語では同じ意味の語を使う。

| 節                   | 入れるもの                                                                                                     |
| -------------------- | -------------------------------------------------------------------------------------------------------------- |
| Pull Request         | userが作成したPR、userがmerge・closeしたPR                                                                     |
| Issue                | userが起票・close・担当設定などをしたIssue                                                                     |
| レビュー             | 他人のPRへのuserのレビューと、レビュー待ちのPR。BotのPRへのapproveは含めず、Pull Request節のBotのgroupに入れる |
| エージェントとの作業 | `sessions.json`のsession                                                                                       |

内容が無い節は作らない。
レビュー待ちは、期間の終了日が今日のときだけ載せる。
Pull Request・Issue・レビューの節はGitHubの情報だけで書き、会話の内容を足さない。

GitHubの節のgroupは次のように分ける。

- Pull Request節はrepoごとにgroupを作り、`label`にrepo名、`theme`に作業のテーマを書く。1つのrepoに無関係なテーマが並ぶならgroupを分ける
- 同じ変更を複数のrepoに入れたPRは、1つのgroupの1行にまとめ、各repoのPRを`links`に並べる。`label`は「全 repo 共通」のように範囲を表す語にする
- BotのPR (`author_is_bot`) は、Pull Request節の最後のgroupへまとめ、1つのrepoを1行で出す。`title`には更新したpackageとversionを並べ、`state`は付けない
- Issue節とレビュー節は、操作の種類でgroupを分ける (例: 起票 (open)、Close したもの、担当に設定、変更を要求、レビュー待ち)
- groupは作業の重さの順に並べる。機能追加・修正、複数repoの共通作業、Botの依存更新の順にする

GitHubの節の各行は次のように書く。

- `title`: PR・Issueのタイトルをそのまま使う。ページが日本語なら、和文と英数字の間に半角スペースを入れる。複数のrepoのitemを含むgroupでは、先頭に「<repo名>: 」を付ける
- `note`: タイトルだけでは分からない背景や効果を、本文から1文で書く。件数・時間・versionなどの数値があれば使う。タイトルで足りる行には付けない。本文は`gh pr view <number> -R <owner>/<repo> --json body`か`gh issue view`で読む
- mergeせずにcloseしたPRには、closeした理由を`note`に書く
- `date`: 期間内の`actions`のうち、行の内容に対応する日付を`MM/DD`で書く。期間内にmergeしたならmerge日、closeしたならclose日、起票と作成なら作成日、レビューならレビュー日を使う
- `state`: PRとIssueは`state`の値 (`merged`、`open`、`closed`。draftなら`draft`)、レビューの行はuserのレビュー結果 (`approved`、`changes_requested`) にする。`current_state`が`state`と違うitemは、その後の状態を`note`に書いてよい

エージェントとの作業の節は次のように書く。

- 1つのsessionを1行にする。月次や四半期で行が多くなる場合は、同じrepoで同じテーマのsessionを1行にまとめ、`note`にsession数を書く
- repoごとにgroupを作り、`label`に`repo`を書く。repoの外のsessionは「repo 外」のgroupにまとめる
- `tag`: `Claude Code`か`Codex`
- `title`: sessionで行ったことを、発話と最後の返答から1文で要約する。`title`フィールドの題名は参考にとどめる
- `note`: 結果や決めたことが分かれば1文で書く
- `links`: `github_refs`のうち、そのsessionで作成・更新したPR・Issue
- `date`: 期間内の日付。複数日にわたるなら`MM/DD–MM/DD`
- 他のsessionから動作確認のために起動された短いsession (作業ディレクトリが一時ディレクトリで発話が1件など) と、この報告を作るだけのsessionは除き、除いた件数をfooterに書く
- 発話や返答を引用せず、要約して書く。secret・token・認証情報と、メールアドレスなどの個人情報は書かない。作業ディレクトリのパスも書かない

各節の行は日付の昇順に並べる。ページ全体の項目は次のように書く。

| 項目      | 書き方                                                                                                                                                                                                                                                                             |
| --------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `title`   | 日次は`<対象名> 日次作業 M/D`、週次は`<対象名> 週次作業 M/D–M/D`、月次は`<対象名> 月次作業 YYYY-MM`、四半期は`<対象名> 四半期作業 YYYY Qn`、任意期間は`<対象名> 作業報告 M/D–M/D`。年をまたぐ期間は日付に年を付ける。英語なら`<subject> weekly work M/D–M/D`のように同じ構成にする |
| `heading` | `title`の期間の部分を`(<user>)`に置き換えたもの                                                                                                                                                                                                                                    |
| `meta`    | `対象期間: YYYY-MM-DD (曜) 〜 YYYY-MM-DD (曜) / <owner> の repo とエージェントとの session`                                                                                                                                                                                        |
| `stats`   | 報告に載せた件数。例: 「PR を merge (うち Bot 9)」「Issue を起票 (open)」「PR に変更を要求」「レビュー待ち」「エージェントとの session」。0件の項目は書かない                                                                                                                      |
| `footer`  | 集計方法 (`queries`の要約、読んだsessionログ、期間、タイムゾーン)、`excluded`のitemとその理由、除いたsessionの件数、前回の報告との重複で除いたitem                                                                                                                                 |

### 5. 描画する

```bash
python3 "<skill-dir>/scripts/render_report.py" "$work_dir/report.json" \
  --out "$work_dir/work-report-<since>-<until>.html"
```

exit codeが2のときは、stderrに違反が1行ずつ出る。report.jsonを直して再実行する。

### 6. 公開する

HTMLをWebページとして公開できるtool (Claude CodeのArtifact toolなど) があれば、描画したHTMLを新しいページとして公開する。前回の報告のページは上書きしない。
無ければHTMLのパスを成果物とする。

### 7. 報告する

- ページのURL、またはHTMLのパス
- 主な件数と主な作業を数行
- 判断したこと: 除外したitemやsessionとその理由、分類に迷ったitem

ページの行をチャットに再掲しない。
