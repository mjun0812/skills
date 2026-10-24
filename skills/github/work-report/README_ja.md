# work-report

[English](README.md)

指定した期間にユーザーが行った作業を、1枚のHTMLの作業報告にする。期間は日・週・月・四半期を選べ、既定は週である。材料はGitHubのowner (orgまたはuser) 配下のPR・Issue・レビューと、Claude Code・Codexとの会話である。

ページはPull Request・Issue・レビュー・エージェントとの作業の4節で、PRはrepoとテーマごとのgroupに並べ、各行に背景を1文で添える。複数のrepoへ入れた同じ変更は1行にまとめ、Botの依存更新はrepoごとの1行で出す。会話はsession単位の行にし、何をしたかを要約する。

集計と描画はscriptが行い、agentはitemの分類と各行の文言だけを書く。そのため、毎回同じ見た目のページになる。

## 使い方

- 「今週の作業を報告書にして」
- 「先月の作業をまとめて」
- 「日報を作って」
- 「四半期の振り返りを作って」

## 引数

| 引数         | 効果                                                                                          |
| ------------ | --------------------------------------------------------------------------------------------- |
| owner        | 集計対象のorgまたはuser。依頼かcwdのgit remoteから決まらなければ確認する                      |
| user         | 作業を集計するユーザー。省略時はghで認証中のユーザー                                          |
| 期間         | 今日・昨日・今週・先週・今月・先月・四半期、または開始日と終了日。省略時は今日を含む直近7日間 |
| タイムゾーン | 期間の境界と日付表示に使うタイムゾーン。省略時は実行環境のローカル                            |
| 対象名       | ページのタイトルに使う名前。省略時はowner名                                                   |
| 前回の報告   | 前回の報告のURLかファイル。渡すと、前回すでに載せたmerge・close・起票のitemを除外する         |

週は月曜始まり、四半期は暦年 (1〜3月がQ1) で数える。別の区切りは依頼で指定できる。

## 動作

- `scripts/collect_activity.py`が、ownerの配下で次の条件に当たるPR・Issueを検索する。
  - userが関与している (作成者・担当・言及・コメント)
  - userがレビューした
  - userへのレビュー依頼が残っている
  - 期間内にcloseされた
- 各itemのtimelineから期間内のuserの操作 (作成、merge、close、レビュー、担当設定など) を拾い、操作が無いitemを除外する。時刻はすべて指定したタイムゾーンへ換算する。
- 検索APIの上限 (1検索1,000件) を超えた場合は警告を出し、agentが期間を分けて集計し直す。
- `scripts/collect_sessions.py`が、Claude CodeとCodexのログから、期間内にユーザーが発話したsessionを集める。ログの場所は`${CLAUDE_CONFIG_DIR:-~/.claude}/projects`と`${CODEX_HOME:-~/.codex}/sessions`である。subagentのthreadと非対話で起動したCodexは除く。それ以外のsessionは、どのrepoで作業したかを問わず対象にする。
- agentがitemとsessionを節とgroupへ分類し、PR・Issueの本文とsessionの発話・返答から文言を書いてreport JSONにする。会話は引用せずに要約し、secret・認証情報・個人情報・作業ディレクトリのパスは書かない。
- `scripts/render_report.py`がreport JSONを検証し、固定のlayoutとstyleでHTMLを描画する。違反があれば1行ずつ報告するため、agentはJSONを直して再実行する。
- HTMLを公開できるtool (Claude CodeのArtifact toolなど) があれば新しいページとして公開し、無ければHTMLのパスを報告する。前回の報告のページは上書きしない。
- PRを経ない直接のpushと、他人のIssueへのlabel付けのような関与の無いitemへの操作は集計しない。行の状態は期間の終了時点のもの、レビュー待ちは実行した時点のものになる。

## 依存

- `gh` CLI (認証済み)
- `python3` (3.11以上、標準libraryのみ)
- `git`: Claude Codeのsessionの作業ディレクトリからrepoを調べるのに使う
- `jq`と`mktemp`: 集計結果の読み出しと作業ディレクトリの作成に使う
- macOSまたはLinux

手順の詳細は[SKILL.md](SKILL.md)を参照。
