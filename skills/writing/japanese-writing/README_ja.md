# japanese-writing

[English](README.md)

日本語の文章を、文書の種類に合った規範で書く、または直す。
[`japanese-tech-writing`](../japanese-tech-writing/README_ja.md)と[`stop-ai-slop-jp`](../stop-ai-slop-jp/README_ja.md)の規範を1つにまとめ、食い違っていた規則を文書の種類ごとに振り分けた。
既にある文章を直すときの規則は、[yomiyasu](https://github.com/nanaism/yomiyasu)を参考にした。

必要な資料はすべて`references/`に同梱しており、単独でinstallしても動作する。

## 使い方

- "日本語で記事を書いて"
- "この文章を推敲して"
- "読みやすく直して"
- "AI臭を消して"

引数は取らない。

## 動作

1. 文書の種類を決める。種類はreference、解説、体験記の3つである。PR説明、障害報告、議事録、メールなど13の細かい種類に当たるときは、その種類でふつうの書き方を残す。
2. 作業の種類を決める。新しく書くなら執筆、既にある文章を直すなら修正である。
3. 種類に対応するreferenceを読む。
4. 執筆では、書いたあとに構造と語彙のカタログで点検して直す。
5. 修正では、原文を初めて読む読み手として通読してから問題を洗い出し、すべて直す。変更点は、原文の引用、修正後の文、理由の組で報告する。

規範どうしがぶつかるときは、次の順に従う。

1. 事実を作らない。
2. AI臭を消す。
3. 書き直した文の意味を変えない。

AI臭のある表現は、中身を原文から書けるなら書き直し、書けなければ語を外すか文ごと削る。削った箇所と、書き手の持つ事実があれば書き足せる箇所は、「要確認」として報告する。

referenceの内容は次のとおり。

- `references/argument.md`: 段落と論証の構成、論証の厳密さ、読み手の負荷、演出の抑制
- `references/rewriting.md`: 既にある文章のどこを直し、どこを残すかを決める規則
- `references/doc-types.md`: 13の細かい種類ごとの、残す書き方と直すもの
- `references/markup.md`: 表、箇条書き、図、散文の使い分け
- `references/structures.md`: 避ける構造のカタログ
- `references/phrases.md`: 避ける語彙のカタログ

## 依存

なし。

## 出典

`references/argument.md`は、k16shikano氏の[原文](https://gist.github.com/k16shikano/fd287c3133457c4fd8f5601d34aa817d)を参考にした。

`references/rewriting.md`と`references/doc-types.md`は、[nanaism/yomiyasu](https://github.com/nanaism/yomiyasu)を参考にした。

手順の詳細は[SKILL.md](SKILL.md)を参照。
