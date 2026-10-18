# yomiyasu-lite

[English](README.md)

AIが書いた日本語の文章を、同梱のlintが警告した箇所だけ、意味を変えずに推敲する。lintは不自然な比喩動詞、AIに多い語、定型の前置きと結び、過剰な太字・箇条書き、絵文字、ダッシュ、文末のコロンなどを検出する。警告の出ていない文は、読みにくく見えても書き換えない。

直すときは、主張、言い切りの強さ、数値・固有名詞・条件、誰が何をするかを原文と同じに保ち、原文にない情報を足さない。これらを保てない言い換えしか無ければ原文を残し、意味が確定できない箇所は書き手への質問にする。主述のずれのような、lintが検出しない構造上の問題は直さない。

AI臭を全体から消して採点まで求める場合は[`stop-ai-slop-jp`](../stop-ai-slop-jp/README_ja.md)を使う。

## 使い方

`disable-model-invocation: true`のskillである。ユーザーが`/yomiyasu-lite`で呼んだときだけ実行し、実行中のagentが自発的に呼ぶことはない。

- `/yomiyasu-lite draft.md`
- `/yomiyasu-lite` に続けて文章を貼る

## 動作

1. 同梱のlintを原文にかける。文書の種類(PR、障害報告、メールなど)が分かれば指定し、その種類で普通の書き方は候補から外す。
2. 候補を1件ずつ判断し、警告文にある「残してよい条件」に当たるものは残す。
3. 残りの候補を、意味を保ったまま書き直す。
4. 最終稿にlintをもう一度かけ、残った警告には残した理由を付ける。

最終稿は原文と同じディレクトリに`<原文の名前>.yomiyasu.md`として保存し、原文は書き換えない。原文の更新を頼まれたときだけ上書きする。返答には保存先と書き直した本文を出し、変えたところ・残した警告・書き手に確かめたい点を添える。commit、push、外部への投稿はしない。

## 依存

- Python 3.14以上(`python3`)。同梱scriptは標準ライブラリだけで動く。

同梱のlint (`scripts/`) は[nanaism/yomiyasu](https://github.com/nanaism/yomiyasu) v2.0.1の`yomiyasu_lint.py`と`markdown_visibility.py`をもとに改変した(MIT License、[LICENSE](LICENSE)を参照。絵文字の判定に使うUnicodeのデータは[UNICODE-LICENSE.txt](UNICODE-LICENSE.txt)を参照)。

手順の詳細は[SKILL.md](SKILL.md)を参照。
