# japanese-writing

[English](README.md)

日本語の文章を、文書の種類に合った規範で書く、または直す。
[`japanese-tech-writing`](../japanese-tech-writing/README_ja.md)、[`cognitive-rhythm-writing`](../cognitive-rhythm-writing/README_ja.md)、[`stop-ai-slop-jp`](../stop-ai-slop-jp/README_ja.md)の規範を1つにまとめ、3つのあいだで食い違っていた規則を文書の種類ごとに振り分けた。

必要な資料はすべて`references/`に同梱しており、単独でinstallしても動作する。

## 使い方

- "日本語で記事を書いて"
- "この文章を推敲して"
- "読みやすく直して"
- "AI臭を消して"

引数は取らない。

## 動作

1. 文書の種類を決める。種類はreference、解説、体験記の3つである。
2. 作業の種類を決める。新しく書くなら執筆、既にある文章を直すなら修正である。
3. 種類に対応するreferenceを読む。
4. 執筆では、書いたあとに構造と語彙のカタログで点検して直す。解説では緩急の点検手順も行う。
5. 修正では、見つけた問題をすべて直してから、変更点を原文の引用、修正後の文、理由の組で報告する。AI臭のある表現は、中身を書けなければ語を外すか文ごと削り、削った箇所を報告する。

文書の種類によって変わる規則は次のとおり。

| 種類      | 該当する文書                                   | 規則の例                                                                     |
| --------- | ---------------------------------------------- | ---------------------------------------------------------------------------- |
| reference | リファレンス、手順書、README、仕様書、PR、報告 | 対象と前提から入る。禁止は言い切って理由を添える。緩急を足さない             |
| 解説      | 技術記事、書籍の章、解説文、論考               | 対象の性質から立てた問いで入ってよい。見出しは疑問形でもよい。緩急を設計する |
| 体験記    | ブログ、エッセイ、体験記、ふりかえり           | 書き手自身の話から入る。確信度を伝える保留は残し、免責は消す                 |

修正に新しい事実(行為者、数値、固有名詞、エピソード、仕様)が必要な箇所は、推測で補わない。語を外すか文を削り、「要確認」として報告する。

referenceの内容は次のとおり。

- `references/argument.md`: 段落と論証の構成、論証の厳密さ、読み手の負荷、演出の抑制
- `references/rhythm.md`: 解説の緩急の設計と、執筆後の点検手順
- `references/structures.md`: 避ける構造のカタログ
- `references/phrases.md`: 避ける語彙のカタログ

## 依存

なし。

## 出典

`references/argument.md`はk16shikano氏の[原文](https://gist.github.com/k16shikano/fd287c3133457c4fd8f5601d34aa817d)を、`references/rhythm.md`は同氏の[原文](https://gist.github.com/k16shikano/eb2929f13ed19c97188393d297be8432)を参考にした。

書き直した文の意味を保つための規則は、[nanaism/yomiyasu](https://github.com/nanaism/yomiyasu)を参考にした。

手順の詳細は[SKILL.md](SKILL.md)を参照。
