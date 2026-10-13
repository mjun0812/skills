# exmd

[English](README.md)

概念・仕組み・調査内容を、frontmatter・要約・目次・用語表・Mermaid図・コードを備えた1枚のMarkdown(GFM)で解説する。GitHub、VS Code、Obsidianでそのまま読める。会話に無い題材でも、調査したうえで解説する。

[`exhtml`](../exhtml/README_ja.md)のMarkdown版であり、HTMLページが必要ならそちらを使う。会話で確立した内容を何も足さずに書き出すなら[`chat-note`](../chat-note/README_ja.md)を使う。

## 使い方

- 「Markdownで解説して」
- 「exmdで作って」
- 「解説記事をMarkdownで」
- 「〜についてMarkdownにまとめて」

## 動作

- 対象を確定し、構成(背景、本論、具体例、補足・限界・関連事項)を決め、先に専門用語を洗い出す。
- `assets/template.md`を埋めて作成する。固定部分(frontmatterの項目、要約・目次・用語の節)は変えない。既存のexmd成果物は、ファイル名を変えず、本文・用語・目次・`updated`だけを更新する。
- `scripts/check_exmd.py`を実行し、`ok`になるまで修正する。scriptは目次と見出しの対応も確かめる。チェックを通っていないファイルは成果物として報告しない。
- 保存先はユーザーの指定に従う。指定が無ければカレントディレクトリに`YYYY-MM-DD-<slug>.md`として保存する。同名ファイルがあれば上書き前に確認する。
- 記法の規則: GFMだけを使い(生のHTML、画像、定義リストは使わない)、絵文字や矢印文字は使わず、Mermaidに色を付けない。図はMermaidで描き、file treeや擬似コードの小さな変更は`diff` fenceで示す。一方向の単純な手順は図にせず番号付きの説明にする。

## 依存

- `japanese-tech-writing` skill: インストールされていれば、文章の規範としてSkill toolで呼ぶ。exmdは構成と記法だけを定める。
- `python3`: チェックscriptの実行に使う。

手順の詳細は[SKILL.md](SKILL.md)を参照。
