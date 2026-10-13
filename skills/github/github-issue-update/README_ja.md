# github-issue-update

[English](README.md)

open issueを横断的に点検し、close(解決済み・重複・stale)、コメント追記(追加すべき情報がある、または本文が現状とズレている)、ラベルの追加/削除の3種類の更新を提案する。最初にsummaryを提示し、ユーザーが承認するまで何も書き込まない。

点検対象はopen issueだけで、closed issueとPRは含めない。1件のissueを深く書き換える場合は[`github-issue-polish`](../github-issue-polish/README_ja.md)を使う。

## 使い方

- 「issueを整理して」
- 「issueのラベルを整理して」

```text
/github-issue-update
/github-issue-update language=en --max 20
```

## 引数

| 引数        | 効果                                               |
| ----------- | -------------------------------------------------- |
| `language`  | 投稿するコメントの言語。デフォルトは`ja`。         |
| `--max <N>` | 1回の実行で反映する候補の上限。デフォルトは`100`。 |

## 動作

- close候補: open issue同士の重複(古い方を残す)、解決済み(完了条件のチェックボックスが全て埋まっている、または参照しているファイル/コードが消失)、stale(最終更新が90日より古く、かつコメント0件または完了条件が抽象的)。
- ラベル変更の候補は、リポジトリに既にあるラベルだけを対象にする。ラベルは新規作成しない。
- 同一issueへの複数のactionは束ねる。優先度は、解決済みclose、重複close、stale close、ラベル変更、コメント追記の順。`--max`を超える分は優先度の低い側から打ち切り、件数を報告する。
- summaryはclose、コメント追記、ラベル変更に分けて提示する。承認は段階的に取る: すべて反映、個別選択、すべてキャンセル、詳細を見たい候補の確認。却下した候補は、スキップとして件数だけ報告する。
- 反映は、同一issueへのactionは直列、異なるissueは5〜10件単位で並列に処理する(rate limitのため20件超のバッチは続けて投げない)。1件失敗しても他は継続し、失敗は報告に集計する。
- closeするissueには、必ず理由コメントを投稿してからcloseする。`gh issue close --comment`は使わず、`gh issue comment`と`gh issue close`を使う。
- 最終報告には、close、コメント追記、ラベル変更、スキップ、打ち切り、失敗の件数を含める。

## 依存

- `gh` CLI(未認証の場合は停止する)

手順の詳細は[SKILL.md](SKILL.md)を参照。
