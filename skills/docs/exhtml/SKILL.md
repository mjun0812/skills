---
name: exhtml
description: >-
  概念・仕組み・調査内容を、用語集・目次・図・コードを備えた1枚の自己完結HTMLで解説するSkill。
  同梱のtemplateを埋めて作成し、既存のexhtml成果物は本文だけを更新する。
  ユーザーが「HTMLで解説して」「exhtmlで作って」「解説ページにして」「HTMLにまとめて」のように依頼したら使うこと。
  Markdownでのまとめ (chat-note) や、図やスライド単体の作成には使わない。
allowed-tools: Read, Write, Edit, Glob, Grep, Bash(python3:*), Bash(date:*), Bash(open:*), Bash(ls:*), Bash(cat:*)
---

# exhtml

## 目的

概念・仕組み・調査内容を、読み手が原文を読まなくても理解できる1枚のHTMLにする。
見た目はtemplateで固定し、agentは内容だけを書く。
用語集を右、目次を左に置き、ダーク既定でライトへ切り替えられる。

## 併用推奨

文章の規範は `japanese-tech-writing` skillに従う (インストールされていれば読む)。
exhtmlは構成と見た目だけを定め、文章の書き方は再定義しない。

## 成果物

- 1枚の自己完結HTML。ビルド不要でブラウザが直接開ける
- 保存先はユーザーの指定に従う。指定が無ければ `/tmp/YYYY-MM-DD-<内容を表す英語slug>.html` として保存する。同名ファイルがあれば上書き前にユーザーに確認する
- 既存のexhtml成果物 (先頭行が `<!-- exhtml template v1 -->`) を更新するときはファイル名を変えず、`updated` だけを書き換える

## 手順

1. 対象を確定する。会話で確立した内容、指定されたファイル、調査結果のどれでもよい。曖昧なら会話全体から推定する
2. 構成を決める。用語 → 背景 → 本論 → 具体例 → 補足・限界・関連事項の順を基本とし、本文で使う専門用語を先に洗い出す
3. 新規なら `assets/template.html` をコピーしてプレースホルダーを埋める。更新なら本文・用語集・`updated` を書き換える。テンプレート部分は触らない
4. 使っていない任意ブロック (mathjax / shiki / mermaid) を削除する
5. 検査scriptを実行し、`ok` になるまで修正する。検査を通していないファイルを成果物として報告しない

   ```bash
   python3 "${CLAUDE_SKILL_DIR}/scripts/check_exhtml.py" <file.html>
   ```

   `${CLAUDE_SKILL_DIR}` が展開されない環境では、このSKILL.mdがあるディレクトリに読み替える

6. macOSなら `open <file.html>` で開く。失敗しても成果物には影響しないので、パスの報告だけで終える
7. 返答は「何を書いたか / 保存先 / 検査結果」に絞り、本文は再掲しない

## テンプレート

場所は `assets/template.html` (Claude Codeでは `${CLAUDE_SKILL_DIR}/assets/template.html`)。

| プレースホルダー | 内容                                                                                       |
| ---------------- | ------------------------------------------------------------------------------------------ |
| `{{TITLE}}`      | h1と `<title>`。主題を平易に名指しする                                                     |
| `{{CREATED}}`    | 作成日 `YYYY-MM-DD` (`date +%Y-%m-%d`)                                                     |
| `{{UPDATED}}`    | 更新日 `YYYY-MM-DD`。新規作成時は作成日と同じ                                              |
| `{{MODEL}}`      | 書いたモデル名 (例: `claude-fable-5-1`)。空白を含めない                                    |
| `{{LEDE}}`       | h1直下のリード文。1〜2文                                                                   |
| `{{SUMMARY}}`    | 冒頭要約の `<li>` を1〜3個                                                                 |
| `{{BODY}}`       | 本文。h2/h3には必ず英語の `id` を付ける (目次はこのidからJSが生成する。目次を手書きしない) |
| `{{GLOSSARY}}`   | 用語集。`<dt id="term-<slug>">用語</dt><dd>定義</dd>` の並び                               |

書き換え禁止の範囲:

- `exhtml:template-begin` から `exhtml:template-end` (`<style>`)。検査scriptがテンプレートとの一致を確認する
- `exhtml:runtime` ブロック (テーマ切替と目次生成)
- ページ固有の `<style>` と `<script>` は書かない。図の配置調整のような最小限の `style` 属性だけ許す

任意ブロックは開始コメントから終了コメントまでを丸ごと削除する。

| ブロック         | 残す条件                                                            |
| ---------------- | ------------------------------------------------------------------- |
| `exhtml:mathjax` | 本文に `$...$` か `$$...$$` の数式がある                            |
| `exhtml:shiki`   | `language-plaintext` 以外の `<pre><code class="language-*">` がある |
| `exhtml:mermaid` | `<pre class="mermaid">` がある                                      |

使える部品 (class名):

| 部品                                                         | 用途                                                                         |
| ------------------------------------------------------------ | ---------------------------------------------------------------------------- |
| `ex-card`, `ex-card-label`, `ex-grid-2`                      | 比較や前提・結果の並置。均一なカードを並べるだけの使い方はしない             |
| `ex-chip`                                                    | 並列の固有名や分類名の列挙にだけ使う。唯一角丸が許される部品                 |
| `ex-note`, `ex-note is-important`                            | 補足と、ページで最重要の注意                                                 |
| `blockquote.ex-quote`, `ex-quote-source`                     | 引用。原文と訳文を同じ文字サイズで上下に並べ、出所を末尾に置く               |
| `ex-rowlabel`                                                | 表の行見出しセル。語中の折り返しを防ぐ                                       |
| `ex-figure`, `ex-figure-frame`, `figcaption`                 | 図の外枠、表示面、図番号と説明                                               |
| `fig-node`, `fig-group`, `fig-edge`, `fig-label`, `fig-wrap` | 手描きSVGの箱、点線グループ、矢印付き線、ラベル、折り返しラベル              |
| `c1`, `c2`, `c3`, `c4`                                       | 図のカテゴリ色。`fig-node` とMermaidのnodeに付ける塗り。両テーマで切り替わる |
| `pre.ex-diff` と `span.ins` / `span.del` / `span.ctx`        | コード差分                                                                   |
| `details` / `summary`                                        | 折りたたみ                                                                   |

## 構成

- h1直後の要約は3項目以内。読み手が要約だけで主題を掴めるようにする
- 用語集は本文で使う専門用語を1〜2文で定義する。広く知られた固有名詞も定義する
- 本文の初出箇所は `<a class="ex-term" href="#term-<slug>">用語</a>` で用語集へリンクする
- 用語集は本文での初出順に並べる。本文からリンクされない用語は末尾に置く
- 説明対象に合わせて、並置、図解、タイムライン、要約、折りたたみを使い分ける
- 一方向の単純な手順は番号付きの説明にし、図にしない
- 表は短い対応関係に使い、3列までを基本とする

## デザイン規則

- 色はtemplateのtokenだけを使う。本文の有彩色はリンク (`a`) と強調 (`em`) の2つに限り、強調は1ページに数箇所まで。差分色とシンタックスハイライトは機能色として例外
- 図の中では、カテゴリや状態を表す塗りにだけ `c1` から `c4` の4色を使える。装飾には使わず、色の意味を `figcaption` に書く。線と文字は色にしない
- 角丸は `.ex-chip` だけ。他で `border-radius` を書かない
- 次を使わない。絵文字、記号文字 (チェックや星)、矢印文字、グラデーション、影、外部画像、装飾目的の色、同じ形のカードを敷き詰めるだけの構成
- 必要な図記号はインラインSVGで描く

## 図

| 内容                                                          | 手段                        |
| ------------------------------------------------------------- | --------------------------- |
| 構成要素と関係 (ノード10個程度まで)、層構造、before/after     | 手描きSVG                   |
| 既存の形に対する小さな変更 (file tree、call tree、擬似コード) | `pre.ex-diff` の差分        |
| 直線的な手順                                                  | 番号付きの説明 (図にしない) |
| 分岐のある処理                                                | Mermaid `flowchart TD`      |
| 複数の登場人物の往復                                          | Mermaid `sequenceDiagram`   |
| テーブル間の関係                                              | Mermaid `erDiagram`         |
| 状態遷移                                                      | Mermaid `stateDiagram-v2`   |

原典に重要な図がある場合は出所を明記してリンクで参照し、模倣図を作らない。

手描きSVGの規則:

- `.ex-figure` > `.ex-figure-frame` > `<svg viewBox="...">` に置き、`figcaption` を付ける
- 線幅と色を自分で指定せず、`fig-*` のclassに任せる。色は `currentColor` でテーマに追従する
- カテゴリを塗りで区別するときは `<rect class="fig-node c1">` のように `c1` から `c4` を付ける。`fill="#..."` や `style` 属性で色を書かない。凡例は同じclassの小さな `rect` で図の中に置くか、`figcaption` に書く
- 箱の幅はラベルから決める。半角1文字8px、全角1文字16px、左右に16pxずつの余白
- 長いラベルは `<foreignObject>` の中に `<div class="fig-wrap">` を置いて折り返す
- viewBoxは内容の外側に16pxの余白を取る
- ノードが多い場合は縦方向に並べる。矢印が交差する構成を避ける

Mermaidの規則:

- `<pre class="mermaid">` を `.ex-figure-frame` の中に置く
- ノードは `id[ラベル]` の角形だけを使う。`id(ラベル)` の角丸は使わない
- ラベルに `<br/>` やタグを書かない。改行が要らない長さまで短くし、説明は `figcaption` に書く
- ノードを塗りで区別するときは `class A,B c1` のように `c1` から `c4` を付ける (flowchartとstateDiagramのみ)。`classDef`、`style`、`linkStyle`、`%%{init}` で色を書かない
- ノードが15個を超えるなら主題ごとに図を分ける

## コード

- `<pre><code class="language-xxx">` に書く。ハイライトしないなら `language-plaintext`
- `<` と `&` はHTMLエスケープする
- 差分は `pre.ex-diff` に行ごとの `span` で書き、変更理由を散文で先に説明する
- 差分にするのは、周囲の形が既にあり、要点が「何が変わるか」のとき。大半が新規なら差分にせずブロック全体を示す
- 差分の対象はコードに限らない。file tree、call tree、擬似コードのような構造のスケッチも `pre.ex-diff` で示す。関係や層構造そのものを示すなら手描きSVGにする

  ```html
  <pre class="ex-diff"><span class="ctx">src/</span>
  <span class="ctx">├── api/</span>
  <span class="del">└── config.ts</span>
  <span class="ins">└── config/</span>
  <span class="ins">    ├── load.ts</span>
  <span class="ins">    └── schema.ts</span></pre>
  ```

## 数式

- インライン数式は `$...$`、ディスプレイ数式は `$$...$$`
- ベクトルと行列は `\boldsymbol{...}`。スカラー、添字、集合名は装飾しない
- `window.MathJax` を再定義しない。`<pre>` と `<code>` の中は数式として処理されない
