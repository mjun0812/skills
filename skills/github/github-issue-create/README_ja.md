# github-issue-create

[English](README.md)

Todo・メモ・バグ報告(と同一会話で確認済みの事実)を、GitHub Issueとして1件起票する。素材に含まれる主張はリポジトリ(外部ツールは公式ドキュメント)で裏取りし、確認済み・推測・未確認に分類してから、下書きを提示して承認を得る。関連Issueを先に検索する。事実の記録だけを行い、解決策の決定はしない。

成果物は、タイトル、Issueテンプレートに沿った本文、ラベルを持つIssue 1件である。既存のissueを「issueだけで実装できる」状態まで書き換える場合は、代わりに[`github-issue-polish`](../github-issue-polish/README_ja.md)を使う。

## 使い方

- 「issue作って」
- 「これIssueにしといて」
- 「調べてからissueにして」
- 「バグ報告を起票して」
- 「Todoを起票して」

```text
/github-issue-create language=ja
```

## 引数

| 引数       | 効果                                                        |
| ---------- | ----------------------------------------------------------- |
| `language` | Issueのタイトルと本文の言語(`ja`, `en`)。デフォルトは`en`。 |

## 動作

- 依頼と会話の内容を下書き素材として使う。依頼に内容がまったく含まれていない場合のみ、自由テキストで概要を尋ねる。
- open/closedの両方でIssueを検索して重複を調べる。同じ問題のopen Issueがある場合は、起票を止めて、それでも新規に作成するかを確認する。関連Issueは`Related to #N`として書く。
- 主張(ファイル、関数、設定キー、エラー文、因果関係)をリポジトリで確認する。外部仕様に依存する主張に限り公式ドキュメントを確認する。確認するのは主張の周辺だけで、原因の深掘りや解決策の比較はしない。
- テンプレートを自動で選ぶ: `bug_report`、`test`、`feature_request`、`research`、`task` (判定が曖昧な場合)。
- テンプレートはリポジトリの`.github/ISSUE_TEMPLATE/`があればそれを使い、なければ`references/ISSUE_TEMPLATE/` (英語)または`references/ISSUE_TEMPLATE_JA/` (日本語)を使う。ラベルはリポジトリに既にあるものだけから選ぶ。
- 情報のないセクションは省略する。推測・未確認の主張は仮説や調査事項として書く。本文に行番号は書かない。
- public repositoryへ投稿するIssueに、privateなrepositoryの情報は書かない。
- 図、diff、tree形式のファイル構成差分を、必要に応じて入れる。規則は[references/visuals.md](references/visuals.md)を参照。
- タイトル、本文、種別、ラベルに加え、確認済み・推測・未確認の内訳、web出典、関連Issueを提示し、承認後にだけ作成する。素材が乏しくタイトルを作れない場合は、下書きの代わりに質問する。
- 作成後にIssueを再取得して下書きと照合し、URL、テンプレート種別、ラベルを報告する。未決事項が残る場合は、実装前に仕様を詰めるよう案内する。

## 依存

- `gh` CLI(`gh auth status`が失敗した場合は停止して認証を案内する)

手順の詳細は[SKILL.md](SKILL.md)を参照。
