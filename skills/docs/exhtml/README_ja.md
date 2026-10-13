# exhtml

[English](README.md)

概念・仕組み・調査内容を、1枚の自己完結HTMLで解説する。左に目次、右に用語集を置き、ダークテーマを既定としてライトへ切り替えられる。インラインSVGまたはMermaidの図とハイライト付きコードを含む。ビルド不要で、ブラウザが直接開ける。

見た目は同梱のtemplateで固定し、agentは内容だけを書く。同種のページをMarkdownで作るなら[`exmd`](../exmd/README_ja.md)を使う。会話で確立した内容をそのまま書き出すなら[`chat-note`](../chat-note/README_ja.md)を使う。図やスライド単体の作成には使わない。

## 使い方

- 「HTMLで解説して」
- 「exhtmlで作って」
- 「解説ページにして」
- 「HTMLにまとめて」

## 動作

- 対象(会話の内容、指定ファイル、調査結果)を確定し、構成を決め、先に専門用語を洗い出す。
- `assets/template.html`を埋めて作成する。テンプレート部分、runtimeブロック(テーマ切替と目次生成)、ページ固有の`<style>`と`<script>`は編集しない。使わない任意ブロック(MathJax, Shiki, Mermaid)は削除する。
- `scripts/check_exhtml.py`を実行し、`ok`になるまで修正する。検査を通していないファイルは成果物として報告しない。
- 保存先はユーザーの指定に従う。指定が無ければ`/tmp/YYYY-MM-DD-<slug>.html`。同名ファイルがあれば上書き前に確認する。既存のexhtml成果物は、ファイル名を変えず、本文・用語集・`updated`だけを更新する。
- macOSでは`open`でファイルを開く。失敗してもパスを報告するだけで終える。
- デザイン規則: 色はtemplateのtokenだけを使い、角丸はchipだけに許し、絵文字・グラデーション・影・外部画像は使わない。図は、構造には手描きSVG、分岐・シーケンス・ER・状態遷移にはMermaidを使う。一方向の単純な手順は図にせず番号付きの説明にする。

## 依存

- `japanese-tech-writing` skill: インストールされていれば、文章の規範としてSkill toolで呼ぶ。exhtmlは構成と見た目だけを定める。
- `python3`: 検査scriptの実行に使う。

手順の詳細は[SKILL.md](SKILL.md)を参照。
