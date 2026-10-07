# Skill作成のベストプラクティス

> agentが発見して使いこなせる、効果的なSkillの書き方を学ぶ。

優れたSkillは簡潔で、構造が整理されており、実際の利用で検証されている。このガイドでは、agentが効果的に発見して使えるSkillを書くための実践的な判断基準を示す。

Skillの仕組みに関する概念的な背景は、[Skills overview](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview)を参照。

## 基本原則

### 簡潔さが重要

[context window](https://platform.claude.com/docs/en/build-with-claude/context-windows)は公共財だ。Skillは、agentが知るべき他のすべての情報とcontext windowを共有する。具体的には次のものが含まれる。

* system prompt
* 会話履歴
* 他のSkillのmetadata
* 実際のリクエスト

Skill内のtokenがすべて、すぐにコストになるわけではない。起動時に事前ロードされるのは、全Skillのmetadata(nameとdescription)だけだ。agentがSKILL.mdを読むのはSkillが関連したときだけで、追加ファイルも必要に応じてしか読まない。それでも、SKILL.mdを簡潔に保つことは重要だ。agentがいったんロードすると、そのtokenはすべて会話履歴や他のcontextと競合する。

**基本的な前提**: agentはすでに非常に賢い

agentがまだ持っていないcontextだけを追加する。情報の一つひとつを次のように問い直す。

* 「agentにこの説明は本当に必要か」
* 「agentがこれを知っていると仮定してよいか」
* 「この段落は、そのtokenコストに見合うか」

**良い例: 簡潔**(約50 token):

````markdown  theme={null}
## PDFのテキストを抽出する

テキスト抽出にはpdfplumberを使う。

```python
import pdfplumber

with pdfplumber.open("file.pdf") as pdf:
    text = pdf.pages[0].extract_text()
```
````

**悪い例: 冗長すぎる**(約150 token):

```markdown  theme={null}
## PDFのテキストを抽出する

PDF(Portable Document Format)は、テキストや画像などの内容を含む
一般的なファイル形式だ。PDFからテキストを抽出するには、ライブラリを
使う必要がある。PDF処理用のライブラリは数多くあるが、使いやすく、
ほとんどの場合にうまく動作するpdfplumberを推奨する。
まず、pipでインストールする必要がある。その後、以下のコードを使える...
```

簡潔な版は、agentがPDFとは何か、ライブラリがどう働くかを知っていると仮定している。

### 適切な自由度を設定する

指示の具体性は、タスクの壊れやすさと変動の大きさに合わせる。

**高い自由度**(テキストによる指示):

次の場合に使う。

* 複数のアプローチが有効
* 判断がcontextに依存する
* ヒューリスティクスがアプローチを導く

例:

```markdown  theme={null}
## コードレビューの手順

1. コードの構造と構成を分析する
2. 潜在的なバグやエッジケースを確認する
3. 可読性と保守性を高める改善案を提案する
4. プロジェクトの規約に沿っているか検証する
```

**中程度の自由度**(疑似コード、またはパラメータ付きのscript):

次の場合に使う。

* 推奨するパターンがある
* ある程度のばらつきは許容できる
* 設定が挙動に影響する

例:

````markdown  theme={null}
## レポートを生成する

このテンプレートを使い、必要に応じてカスタマイズする。

```python
def generate_report(data, format="markdown", include_charts=True):
    # データを処理する
    # 指定された形式で出力を生成する
    # 必要に応じて可視化を含める
```
````

**低い自由度**(特定のscript、パラメータが少ない、またはなし):

次の場合に使う。

* 操作が壊れやすく、エラーを起こしやすい
* 一貫性が不可欠
* 特定の順序に従う必要がある

例:

````markdown  theme={null}
## データベースマイグレーション

次のscriptを、そのまま実行する。

```bash
python scripts/migrate.py --verify --backup
```

コマンドを変更したり、flagを追加したりしないこと。
````

**例え**: agentを、道を探索するロボットだと考える。

* **両側が崖の細い橋**: 安全な進路は一つしかない。具体的なガードレールと正確な指示を与える(低い自由度)。例: 正確な順序で実行しなければならないデータベースマイグレーション。
* **危険のない開けた野原**: 成功に至る道は多い。大まかな方向だけを示し、最適な経路はagentに任せる(高い自由度)。例: contextによって最適なアプローチが決まるコードレビュー。

### 使う予定のすべてのモデルでテストする

Skillはモデルへの追加要素として働くため、効果は基盤となるモデルに依存する。使う予定のすべてのモデルでSkillをテストする。

**モデル別のテスト観点**:

* **Claude Haiku**(高速、経済的): Skillは十分なガイダンスを与えているか
* **Claude Sonnet**(バランス型): Skillは明確で効率的か
* **Claude Opus**(強力な推論): Skillは説明過多になっていないか

Opusで完璧に動くものが、Haikuではより詳細な記述を必要とすることがある。Skillを複数のモデルで使う予定なら、すべてのモデルでうまく動く指示を目指す。

## Skillの構造

<Note>
  **YAML frontmatter**: SKILL.mdのfrontmatterには2つのフィールドが必要だ。

  * `name` - Skillの人間可読な名前(最大64文字)
  * `description` - Skillが何をするか、いつ使うかを1行で述べた説明(最大1024文字)

  Skillの構造の詳細は、[Skills overview](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview#skill-structure)を参照。
</Note>

### 命名規則

一貫した命名パターンを使うと、Skillを参照したり議論したりしやすくなる。Skillの名前には**動名詞形**(動詞 + -ing)を推奨する。Skillが提供する活動や能力を明確に表せるためだ。

**良い命名の例(動名詞形)**:

* "Processing PDFs"
* "Analyzing spreadsheets"
* "Managing databases"
* "Testing code"
* "Writing documentation"

**許容できる代替案**:

* 名詞句: "PDF Processing", "Spreadsheet Analysis"
* 動作指向: "Process PDFs", "Analyze Spreadsheets"

**避けるもの**:

* 曖昧な名前: "Helper", "Utils", "Tools"
* 汎用的すぎる名前: "Documents", "Data", "Files"
* skillコレクション内で一貫しないパターン

一貫した命名には次の利点がある。

* ドキュメントや会話でSkillを参照しやすい
* Skillが何をするか、ひと目で分かる
* 複数のSkillを整理して検索しやすい
* プロフェッショナルで統一感のあるskillライブラリを保てる

### 効果的なdescriptionを書く

`description`フィールドはSkillの発見を可能にする。Skillが何をするかと、いつ使うかの両方を含めること。

<Warning>
  **必ず三人称で書くこと**。descriptionはsystem promptに注入されるため、視点が一貫していないと発見に問題が生じることがある。

  * **良い例:** "Processes Excel files and generates reports"
  * **避ける:** "I can help you process Excel files"
  * **避ける:** "You can use this to process Excel files"
</Warning>

**具体的に書き、キーワードを含める**。Skillが何をするかに加えて、いつ使うかを示す具体的なトリガーやcontextも含める。

各Skillのdescriptionフィールドはちょうど1つだ。descriptionはskillの選択に決定的に重要で、agentは100以上になりうる利用可能なSkillの中から適切なものを選ぶためにこれを使う。descriptionには、agentがこのSkillを選ぶべきときを判断できるだけの詳細が必要で、実装の詳細はSKILL.mdの残りの部分が提供する。

効果的な例:

**PDF Processing skill:**

```yaml  theme={null}
description: Extract text and tables from PDF files, fill forms, merge documents. Use when working with PDF files or when the user mentions PDFs, forms, or document extraction.
```

**Excel Analysis skill:**

```yaml  theme={null}
description: Analyze Excel spreadsheets, create pivot tables, generate charts. Use when analyzing Excel files, spreadsheets, tabular data, or .xlsx files.
```

**Git Commit Helper skill:**

```yaml  theme={null}
description: Generate descriptive commit messages by analyzing git diffs. Use when the user asks for help writing commit messages or reviewing staged changes.
```

次のような曖昧なdescriptionは避ける。

```yaml  theme={null}
description: Helps with documents
```

```yaml  theme={null}
description: Processes data
```

```yaml  theme={null}
description: Does stuff with files
```

### 段階的開示のパターン

SKILL.mdは概要として機能し、新人向けガイドの目次のように、必要に応じてagentを詳細な資料へ導く。段階的開示(progressive disclosure)の仕組みについては、overviewの[How Skills work](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview#how-skills-work)を参照。

**実践的なガイダンス:**

* 最適なパフォーマンスのため、SKILL.mdの本文は500行未満に保つ
* この上限に近づいたら、内容を別ファイルに分割する
* 以下のパターンを使って、指示、コード、リソースを効果的に整理する

#### 視覚的な概要: 単純なものから複雑なものへ

基本的なSkillは、metadataと指示を含むSKILL.mdファイル1つから始まる。

<img src="https://mintcdn.com/anthropic-claude-docs/4Bny2bjzuGBK7o00/images/agent-skills-simple-file.png?fit=max&auto=format&n=4Bny2bjzuGBK7o00&q=85&s=87782ff239b297d9a9e8e1b72ed72db9" alt="YAML frontmatterとmarkdown本文を示す単純なSKILL.mdファイル" data-og-width="2048" width="2048" data-og-height="1153" height="1153" data-path="images/agent-skills-simple-file.png" data-optimize="true" data-opv="3" srcset="https://mintcdn.com/anthropic-claude-docs/4Bny2bjzuGBK7o00/images/agent-skills-simple-file.png?w=280&fit=max&auto=format&n=4Bny2bjzuGBK7o00&q=85&s=c61cc33b6f5855809907f7fda94cd80e 280w, https://mintcdn.com/anthropic-claude-docs/4Bny2bjzuGBK7o00/images/agent-skills-simple-file.png?w=560&fit=max&auto=format&n=4Bny2bjzuGBK7o00&q=85&s=90d2c0c1c76b36e8d485f49e0810dbfd 560w, https://mintcdn.com/anthropic-claude-docs/4Bny2bjzuGBK7o00/images/agent-skills-simple-file.png?w=840&fit=max&auto=format&n=4Bny2bjzuGBK7o00&q=85&s=ad17d231ac7b0bea7e5b4d58fb4aeabb 840w, https://mintcdn.com/anthropic-claude-docs/4Bny2bjzuGBK7o00/images/agent-skills-simple-file.png?w=1100&fit=max&auto=format&n=4Bny2bjzuGBK7o00&q=85&s=f5d0a7a3c668435bb0aee9a3a8f8c329 1100w, https://mintcdn.com/anthropic-claude-docs/4Bny2bjzuGBK7o00/images/agent-skills-simple-file.png?w=1650&fit=max&auto=format&n=4Bny2bjzuGBK7o00&q=85&s=0e927c1af9de5799cfe557d12249f6e6 1650w, https://mintcdn.com/anthropic-claude-docs/4Bny2bjzuGBK7o00/images/agent-skills-simple-file.png?w=2500&fit=max&auto=format&n=4Bny2bjzuGBK7o00&q=85&s=46bbb1a51dd4c8202a470ac8c80a893d 2500w" />

Skillが成長したら、agentが必要なときだけロードする追加コンテンツを同梱できる。

<img src="https://mintcdn.com/anthropic-claude-docs/4Bny2bjzuGBK7o00/images/agent-skills-bundling-content.png?fit=max&auto=format&n=4Bny2bjzuGBK7o00&q=85&s=a5e0aa41e3d53985a7e3e43668a33ea3" alt="reference.mdやforms.mdなどの追加の参照ファイルを同梱する" data-og-width="2048" width="2048" data-og-height="1327" height="1327" data-path="images/agent-skills-bundling-content.png" data-optimize="true" data-opv="3" srcset="https://mintcdn.com/anthropic-claude-docs/4Bny2bjzuGBK7o00/images/agent-skills-bundling-content.png?w=280&fit=max&auto=format&n=4Bny2bjzuGBK7o00&q=85&s=f8a0e73783e99b4a643d79eac86b70a2 280w, https://mintcdn.com/anthropic-claude-docs/4Bny2bjzuGBK7o00/images/agent-skills-bundling-content.png?w=560&fit=max&auto=format&n=4Bny2bjzuGBK7o00&q=85&s=dc510a2a9d3f14359416b706f067904a 560w, https://mintcdn.com/anthropic-claude-docs/4Bny2bjzuGBK7o00/images/agent-skills-bundling-content.png?w=840&fit=max&auto=format&n=4Bny2bjzuGBK7o00&q=85&s=82cd6286c966303f7dd914c28170e385 840w, https://mintcdn.com/anthropic-claude-docs/4Bny2bjzuGBK7o00/images/agent-skills-bundling-content.png?w=1100&fit=max&auto=format&n=4Bny2bjzuGBK7o00&q=85&s=56f3be36c77e4fe4b523df209a6824c6 1100w, https://mintcdn.com/anthropic-claude-docs/4Bny2bjzuGBK7o00/images/agent-skills-bundling-content.png?w=1650&fit=max&auto=format&n=4Bny2bjzuGBK7o00&q=85&s=d22b5161b2075656417d56f41a74f3dd 1650w, https://mintcdn.com/anthropic-claude-docs/4Bny2bjzuGBK7o00/images/agent-skills-bundling-content.png?w=2500&fit=max&auto=format&n=4Bny2bjzuGBK7o00&q=85&s=3dd4bdd6850ffcc96c6c45fcb0acd6eb 2500w" />

Skillのディレクトリ構造全体は、次のようになる。

```
pdf/
├── SKILL.md              # メインの指示(トリガー時にロード)
├── FORMS.md              # フォーム入力ガイド(必要に応じてロード)
├── reference.md          # APIリファレンス(必要に応じてロード)
├── examples.md           # 使用例(必要に応じてロード)
└── scripts/
    ├── analyze_form.py   # ユーティリティscript(実行する。ロードはしない)
    ├── fill_form.py      # フォーム入力script
    └── validate.py       # 検証script
```

#### パターン1: 参照付きの高レベルガイド

````markdown  theme={null}
---
name: PDF Processing
description: Extracts text and tables from PDF files, fills forms, and merges documents. Use when working with PDF files or when the user mentions PDFs, forms, or document extraction.
---

# PDF Processing

## クイックスタート

pdfplumberでテキストを抽出する。
```python
import pdfplumber
with pdfplumber.open("file.pdf") as pdf:
    text = pdf.pages[0].extract_text()
```

## 高度な機能

**フォーム入力**: 完全なガイドは[FORMS.md](FORMS.md)を参照
**APIリファレンス**: 全メソッドは[REFERENCE.md](REFERENCE.md)を参照
**例**: よくあるパターンは[EXAMPLES.md](EXAMPLES.md)を参照
````

agentは、FORMS.md、REFERENCE.md、EXAMPLES.mdを必要なときだけロードする。

#### パターン2: ドメイン別の構成

複数のドメインを扱うSkillでは、無関係なcontextのロードを避けるため、ドメインごとに内容を整理する。ユーザーが売上指標について尋ねたとき、agentが読む必要があるのは売上関連のスキーマだけで、財務やマーケティングのデータは不要だ。これによりtoken使用量が抑えられ、contextが絞り込まれる。

```
bigquery-skill/
├── SKILL.md (概要とナビゲーション)
└── reference/
    ├── finance.md (収益、請求の指標)
    ├── sales.md (商談、パイプライン)
    ├── product.md (API利用状況、機能)
    └── marketing.md (キャンペーン、アトリビューション)
```

````markdown SKILL.md theme={null}
# BigQueryデータ分析

## 利用可能なデータセット

**財務**: 収益、ARR、請求 → [reference/finance.md](reference/finance.md)を参照
**営業**: 商談、パイプライン、アカウント → [reference/sales.md](reference/sales.md)を参照
**プロダクト**: API利用状況、機能、導入 → [reference/product.md](reference/product.md)を参照
**マーケティング**: キャンペーン、アトリビューション、メール → [reference/marketing.md](reference/marketing.md)を参照

## クイック検索

grepで特定の指標を探す。

```bash
grep -i "revenue" reference/finance.md
grep -i "pipeline" reference/sales.md
grep -i "api usage" reference/product.md
```
````

#### パターン3: 条件付きの詳細

基本的な内容を示し、高度な内容へはリンクする。

```markdown  theme={null}
# DOCX処理

## ドキュメントの作成

新規ドキュメントにはdocx-jsを使う。[DOCX-JS.md](DOCX-JS.md)を参照。

## ドキュメントの編集

単純な編集では、XMLを直接変更する。

**変更履歴の場合**: [REDLINING.md](REDLINING.md)を参照
**OOXMLの詳細**: [OOXML.md](OOXML.md)を参照
```

agentは、ユーザーがそれらの機能を必要としたときだけ、REDLINING.mdやOOXML.mdを読む。

### 深くネストした参照を避ける

参照されたファイルからさらに別のファイルが参照されている場合、agentはファイルを部分的にしか読まないことがある。ネストした参照に出会うと、agentはファイル全体を読む代わりに`head -100`のようなコマンドで内容をプレビューすることがあり、その結果、情報が不完全になる。

**参照はSKILL.mdから1階層までに保つ**。agentが必要なときにファイル全体を確実に読めるよう、すべての参照ファイルはSKILL.mdから直接リンクする。

**悪い例: 深すぎる**:

```markdown  theme={null}
# SKILL.md
[advanced.md](advanced.md)を参照...

# advanced.md
[details.md](details.md)を参照...

# details.md
実際の情報はここにある...
```

**良い例: 1階層**:

```markdown  theme={null}
# SKILL.md

**基本的な使い方**: [SKILL.md内の指示]
**高度な機能**: [advanced.md](advanced.md)を参照
**APIリファレンス**: [reference.md](reference.md)を参照
**例**: [examples.md](examples.md)を参照
```

### 長い参照ファイルには目次を付ける

100行を超える参照ファイルには、先頭に目次を含める。これにより、agentが部分読み込みでプレビューしても、利用可能な情報の全体像を把握できる。

**例**:

```markdown  theme={null}
# APIリファレンス

## 目次
- 認証とセットアップ
- コアメソッド(作成、読み取り、更新、削除)
- 高度な機能(バッチ操作、webhook)
- エラー処理のパターン
- コード例

## 認証とセットアップ
...

## コアメソッド
...
```

agentは、ファイル全体を読むことも、必要な節へ直接移動することもできる。

このファイルシステムベースのアーキテクチャが段階的開示をどう可能にするかの詳細は、下の「応用」の節にある[実行環境](#実行環境)の節を参照。

## ワークフローとフィードバックループ

### 複雑なタスクにはワークフローを使う

複雑な操作は、明確で順序立ったステップに分解する。特に複雑なワークフローでは、agentが自分の応答にコピーし、進めながらチェックを付けられるチェックリストを用意する。

**例1: 調査の統合ワークフロー**(codeを含まないSkill向け):

````markdown  theme={null}
## 調査の統合ワークフロー

このチェックリストをコピーして、進捗を記録する。

```
Research Progress:
- [ ] Step 1: Read all source documents
- [ ] Step 2: Identify key themes
- [ ] Step 3: Cross-reference claims
- [ ] Step 4: Create structured summary
- [ ] Step 5: Verify citations
```

**Step 1: すべてのソース文書を読む**

`sources/`ディレクトリ内の各文書を確認する。主な論点と裏付けとなる証拠を記録する。

**Step 2: 主要なテーマを特定する**

ソース間のパターンを探す。繰り返し現れるテーマは何か。ソースが一致する点、食い違う点はどこか。

**Step 3: 主張を相互に照合する**

主要な主張ごとに、ソース資料に現れることを検証する。各論点をどのソースが裏付けるかを記録する。

**Step 4: 構造化された要約を作成する**

調査結果をテーマ別に整理する。次を含める。
- 主要な主張
- ソースからの裏付けとなる証拠
- 対立する見解(ある場合)

**Step 5: 引用を検証する**

すべての主張が正しいソース文書を参照していることを確認する。引用が不完全なら、Step 3に戻る。
````

この例は、codeを必要としない分析タスクにもワークフローを適用できることを示している。チェックリストのパターンは、複雑で複数ステップのあらゆるプロセスに使える。

**例2: PDFフォーム入力ワークフロー**(codeを含むSkill向け):

````markdown  theme={null}
## PDFフォーム入力ワークフロー

このチェックリストをコピーして、完了した項目にチェックを付ける。

```
Task Progress:
- [ ] Step 1: Analyze the form (run analyze_form.py)
- [ ] Step 2: Create field mapping (edit fields.json)
- [ ] Step 3: Validate mapping (run validate_fields.py)
- [ ] Step 4: Fill the form (run fill_form.py)
- [ ] Step 5: Verify output (run verify_output.py)
```

**Step 1: フォームを分析する**

実行: `python scripts/analyze_form.py input.pdf`

フォームのフィールドとその位置を抽出し、`fields.json`に保存する。

**Step 2: フィールドマッピングを作成する**

`fields.json`を編集し、各フィールドの値を追加する。

**Step 3: マッピングを検証する**

実行: `python scripts/validate_fields.py fields.json`

続行する前に、検証エラーをすべて修正する。

**Step 4: フォームに入力する**

実行: `python scripts/fill_form.py input.pdf fields.json output.pdf`

**Step 5: 出力を検証する**

実行: `python scripts/verify_output.py output.pdf`

検証に失敗した場合は、Step 2に戻る。
````

明確なステップがあれば、agentが重要な検証を飛ばすことを防げる。チェックリストは、複数ステップのワークフローの進捗を、あなたとagentの双方が追跡する助けになる。

### フィードバックループを実装する

**一般的なパターン**: validatorを実行 → エラーを修正 → 繰り返す

このパターンは出力の品質を大きく向上させる。

**例1: スタイルガイドへの準拠**(codeを含まないSkill向け):

```markdown  theme={null}
## コンテンツのレビュー手順

1. STYLE_GUIDE.mdのガイドラインに従って内容を下書きする
2. チェックリストと照らし合わせてレビューする
   - 用語の一貫性を確認する
   - 例が標準の形式に従っていることを検証する
   - 必須の節がすべて存在することを確認する
3. 問題が見つかった場合
   - 該当する節を示して、各問題を記録する
   - 内容を修正する
   - チェックリストを再度確認する
4. すべての要件を満たしたときだけ次へ進む
5. ドキュメントを確定して保存する
```

これは、scriptの代わりに参照文書を使った検証ループのパターンを示している。「validator」はSTYLE\_GUIDE.mdで、agentはそれを読んで比較することでチェックを行う。

**例2: ドキュメント編集の手順**(codeを含むSkill向け):

```markdown  theme={null}
## ドキュメント編集の手順

1. `word/document.xml`を編集する
2. **すぐに検証する**: `python ooxml/scripts/validate.py unpacked_dir/`
3. 検証に失敗した場合
   - エラーメッセージを注意深く確認する
   - XMLの問題を修正する
   - 再度検証を実行する
4. **検証に通ったときだけ次へ進む**
5. 再構築する: `python ooxml/scripts/pack.py unpacked_dir/ output.docx`
6. 出力ドキュメントをテストする
```

検証ループは、エラーを早期に捕捉する。

## コンテンツのガイドライン

### 時間依存の情報を避ける

古くなる情報は含めない。

**悪い例: 時間依存**(誤りになる):

```markdown  theme={null}
2025年8月より前にこの作業を行う場合は、旧APIを使う。
2025年8月以降は、新APIを使う。
```

**良い例**(「旧パターン」の節を使う):

```markdown  theme={null}
## 現在の方法

v2 APIエンドポイントを使う: `api.example.com/v2/messages`

## 旧パターン

<details>
<summary>旧v1 API(2025-08に非推奨)</summary>

v1 APIは次を使っていた: `api.example.com/v1/messages`

このエンドポイントはサポートされていない。
</details>
```

旧パターンの節は、本文を散らかすことなく、過去の経緯を伝える。

### 一貫した用語を使う

1つの用語を選び、Skill全体で使い通す。

**良い例 - 一貫している**:

* 常に"API endpoint"
* 常に"field"
* 常に"extract"

**悪い例 - 一貫していない**:

* "API endpoint"、"URL"、"API route"、"path"を混ぜる
* "field"、"box"、"element"、"control"を混ぜる
* "extract"、"pull"、"get"、"retrieve"を混ぜる

一貫性は、agentが指示を理解して従う助けになる。

## よくあるパターン

### テンプレートパターン

出力形式のテンプレートを用意する。厳密さのレベルは、必要に合わせる。

**厳密な要件がある場合**(APIレスポンスやデータ形式など):

````markdown  theme={null}
## レポートの構成

必ずこのテンプレート構造を正確に使うこと。

```markdown
# [分析タイトル]

## エグゼクティブサマリー
[主要な調査結果を1段落で概観]

## 主要な調査結果
- 裏付けデータを伴う調査結果1
- 裏付けデータを伴う調査結果2
- 裏付けデータを伴う調査結果3

## 推奨事項
1. 具体的で実行可能な推奨事項
2. 具体的で実行可能な推奨事項
```
````

**柔軟なガイダンスの場合**(適応が有用なとき):

````markdown  theme={null}
## レポートの構成

妥当なデフォルトの形式を示すが、分析に基づいて最善の判断をすること。

```markdown
# [分析タイトル]

## エグゼクティブサマリー
[概要]

## 主要な調査結果
[発見した内容に応じて節を調整する]

## 推奨事項
[具体的なcontextに合わせる]
```

分析の種類に応じて、必要に合わせて節を調整する。
````

### 例のパターン

出力の品質が例を見ることに左右されるSkillでは、通常のpromptと同じように、入力と出力のペアを示す。

````markdown  theme={null}
## コミットメッセージの形式

次の例に従ってコミットメッセージを生成する。

**例1:**
入力: JWTトークンによるユーザー認証を追加した
出力:
```
feat(auth): implement JWT-based authentication

Add login endpoint and token validation middleware
```

**例2:**
入力: レポートで日付が正しく表示されないバグを修正した
出力:
```
fix(reports): correct date formatting in timezone conversion

Use UTC timestamps consistently across report generation
```

**例3:**
入力: 依存関係を更新し、エラー処理をリファクタリングした
出力:
```
chore: update dependencies and refactor error handling

- Upgrade lodash to 4.17.21
- Standardize error response format across endpoints
```

このスタイルに従う: type(scope): 簡潔な説明、その後に詳細な説明。
````

例は、説明だけの場合よりも、望ましいスタイルと詳細度をagentに明確に伝える。

### 条件付きワークフローのパターン

判断の分岐点でagentを導く。

```markdown  theme={null}
## ドキュメント変更ワークフロー

1. 変更の種類を判断する

   **新しいコンテンツを作成するか。** → 下の「作成ワークフロー」に従う
   **既存のコンテンツを編集するか。** → 下の「編集ワークフロー」に従う

2. 作成ワークフロー
   - docx-jsライブラリを使う
   - ドキュメントをゼロから構築する
   - .docx形式でエクスポートする

3. 編集ワークフロー
   - 既存のドキュメントを展開する
   - XMLを直接変更する
   - 変更のたびに検証する
   - 完了したら再パックする
```

<Tip>
  ワークフローが大きくなったり、ステップが多く複雑になったりした場合は、別ファイルに切り出し、タスクに応じて適切なファイルを読むようagentに指示することを検討する。
</Tip>

## 評価と反復

### 先に評価を作る

**大量のドキュメントを書く前に、評価を作成する。** これにより、Skillが想像上の問題ではなく実際の問題を解決することを確実にできる。

**評価駆動開発:**

1. **ギャップを特定する**: Skillなしで、代表的なタスクをagentに実行させる。具体的な失敗や不足しているcontextを記録する
2. **評価を作成する**: これらのギャップをテストする3つのシナリオを作る
3. **ベースラインを確立する**: Skillなしでのagentの性能を測定する
4. **最小限の指示を書く**: ギャップに対処し、評価に通るのに足るだけの内容を作る
5. **反復する**: 評価を実行し、ベースラインと比較して、改善する

このアプローチにより、実現しないかもしれない要件を先読みするのではなく、実際の問題を解決していることを確実にできる。

**評価の構造**:

```json  theme={null}
{
  "skills": ["pdf-processing"],
  "query": "Extract all text from this PDF file and save it to output.txt",
  "files": ["test-files/document.pdf"],
  "expected_behavior": [
    "Successfully reads the PDF file using an appropriate PDF processing library or command-line tool",
    "Extracts text content from all pages in the document without missing any pages",
    "Saves the extracted text to a file named output.txt in a clear, readable format"
  ]
}
```

<Note>
  この例は、単純なテストルーブリックを用いたデータ駆動の評価を示している。これらの評価を実行する組み込みの方法は現時点では提供していない。ユーザーは自分で評価システムを作成できる。評価は、Skillの有効性を測るための信頼できる基準(source of truth)になる。
</Note>

### agentと一緒にSkillを反復的に開発する

最も効果的なSkill開発プロセスには、agent自身が関わる。1つのインスタンス(「Agent A」)と作業して、他のインスタンス(「Agent B」)が使うSkillを作る。Agent Aが指示の設計と改善を助け、Agent Bが実際のタスクでそれをテストする。これが機能するのは、基盤となるモデルが、効果的なagent向けの指示の書き方と、agentが必要とする情報の両方を理解しているからだ。

**新しいSkillを作る場合:**

1. **Skillなしでタスクを完了する**: 通常のpromptでAgent Aと一緒に問題を解く。作業するうちに、自然とcontextを提供し、好みを説明し、手続き的な知識を共有することになる。何度も繰り返し提供している情報に注目する。

2. **再利用できるパターンを特定する**: タスクの完了後、将来の類似タスクにも役立つcontextとして何を提供したかを特定する。

   **例**: BigQueryの分析を行った場合、テーブル名、フィールド定義、フィルタリングのルール(「テストアカウントは常に除外する」など)、よく使うクエリパターンを提供したかもしれない。

3. **Agent AにSkillを作るよう依頼する**: 「今使ったこのBigQuery分析のパターンを記録するSkillを作って。テーブルスキーマ、命名規則、テストアカウントを除外するルールを含めて。」

   <Tip>
     最近のagentは、Skillの形式と構造をもともと理解している。Skill作成の助けを得るために、特別なsystem promptや「Skillを書くためのskill」は必要ない。agentにSkillを作るよう頼むだけで、適切なfrontmatterと本文を持つ、正しく構造化されたSKILL.mdの内容が生成される。
   </Tip>

4. **簡潔さをレビューする**: Agent Aが不要な説明を追加していないか確認する。「勝率とは何かの説明は削除して。agentはすでに知っているから。」と依頼する。

5. **情報アーキテクチャを改善する**: Agent Aに、内容をより効果的に整理するよう依頼する。例: 「テーブルスキーマは別の参照ファイルにまとめて。今後テーブルが増えるかもしれないから。」

6. **類似のタスクでテストする**: Skillをロードした新しいインスタンスであるAgent Bで、関連するユースケースにそのSkillを使う。Agent Bが適切な情報を見つけ、ルールを正しく適用し、タスクをうまくこなせるかを観察する。

7. **観察に基づいて反復する**: Agent Bがつまずいたり、何かを見落としたりした場合は、具体的な内容を持ってAgent Aに戻る。「このSkillを使ったとき、agentが第4四半期の日付フィルタを忘れた。日付フィルタのパターンに関する節を追加すべきか。」

**既存のSkillを改善する場合:**

Skillの改善でも同じ階層的なパターンが続く。次の間を行き来する。

* **Agent Aと作業する**(Skillの改善を助ける専門家)
* **Agent Bでテストする**(Skillを使って実際の作業を行うagent)
* **Agent Bの挙動を観察し**、得られた知見をAgent Aに持ち帰る

1. **実際のワークフローでSkillを使う**: Skillをロードしたagent Bに、テストシナリオではなく実際のタスクを与える

2. **Agent Bの挙動を観察する**: どこでつまずき、どこで成功し、どこで予期しない選択をしたかを記録する

   **観察の例**: 「Agent Bに地域別の売上レポートを依頼したとき、Skillにこのルールが書いてあるのに、クエリは書いたもののテストアカウントの除外を忘れた。」

3. **改善のためにAgent Aに戻る**: 現在のSKILL.mdを共有し、観察した内容を説明する。「Agent Bに地域別レポートを依頼したとき、テストアカウントのフィルタを忘れた。Skillにはフィルタについて書いてあるが、目立ち方が足りないのかもしれない。」と依頼する。

4. **Agent Aの提案をレビューする**: Agent Aは、ルールをより目立たせる再構成、「always filter」ではなく「MUST filter」のようなより強い表現の使用、ワークフローの節の再構成などを提案するかもしれない。

5. **変更を適用してテストする**: Agent Aの改善案でSkillを更新し、類似のリクエストでAgent Bにもう一度テストさせる

6. **使用状況に基づいて繰り返す**: 新しいシナリオに出会うたびに、この観察、改善、テストのサイクルを続ける。各反復は、想定ではなく、実際のagentの挙動に基づいてSkillを改善する。

**チームのフィードバックを集める:**

1. Skillをチームメイトと共有し、使い方を観察する
2. 次を尋ねる: Skillは期待どおりに起動するか。指示は明確か。何が足りないか
3. フィードバックを取り入れて、自分の使い方では見えない盲点に対処する

**このアプローチが有効な理由**: Agent Aはagentが必要とするものを理解しており、あなたはドメインの専門知識を提供し、Agent Bは実際の使用を通じてギャップを明らかにする。そして、反復的な改善により、想定ではなく観察された挙動に基づいてSkillが良くなる。

### agentがSkillをどうナビゲートするかを観察する

Skillを反復する際は、agentが実際にSkillをどう使うかに注意を払う。次の点に注目する。

* **予期しない探索経路**: agentが、想定していない順序でファイルを読んでいないか。構造が、考えていたほど直感的でない可能性がある
* **見落とされたつながり**: agentが重要なファイルへの参照をたどれていないか。リンクをより明示的に、または目立つようにする必要があるかもしれない
* **特定の節への過度な依存**: agentが同じファイルを繰り返し読む場合は、その内容をメインのSKILL.mdに入れるべきかを検討する
* **無視されたコンテンツ**: agentが同梱ファイルに一度もアクセスしない場合、そのファイルは不要か、メインの指示での案内が不十分な可能性がある

想定ではなく、これらの観察に基づいて反復する。Skillのmetadataの'name'と'description'は特に重要だ。agentは、現在のタスクに応じてSkillを起動するかどうかを判断する際にこれらを使う。Skillが何をするか、いつ使うべきかを明確に記述すること。

## 避けるべきアンチパターン

### Windows形式のパスを避ける

Windowsでも、ファイルパスには常にスラッシュを使う。

* ✓ **良い**: `scripts/helper.py`, `reference/guide.md`
* ✗ **避ける**: `scripts\helper.py`, `reference\guide.md`

Unix形式のパスはすべてのプラットフォームで動作するが、Windows形式のパスはUnix系システムでエラーを引き起こす。

### 選択肢を提示しすぎない

必要がない限り、複数のアプローチを提示しない。

````markdown  theme={null}
**悪い例: 選択肢が多すぎる**(混乱を招く):
"pypdfでも、pdfplumberでも、PyMuPDFでも、pdf2imageでも使える..."

**良い例: デフォルトを示す**(抜け道付き):
"テキスト抽出にはpdfplumberを使う。
```python
import pdfplumber
```

OCRが必要なスキャンされたPDFには、代わりにpdf2imageとpytesseractを使う。"
````

## 応用: 実行可能なコードを含むSkill

以下の節は、実行可能なscriptを含むSkillを対象にしている。Skillがmarkdownの指示だけを使うなら、[効果的なSkillのチェックリスト](#効果的なskillのチェックリスト)まで読み飛ばしてよい。

### 解決する。agentに丸投げしない

Skill用のscriptを書くときは、エラー条件をagentに丸投げせず、scriptの中で処理する。

**良い例: エラーを明示的に処理する**:

```python  theme={null}
def process_file(path):
    """ファイルを処理する。存在しなければ作成する。"""
    try:
        with open(path) as f:
            return f.read()
    except FileNotFoundError:
        # 失敗させず、デフォルトの内容でファイルを作成する
        print(f"File {path} not found, creating default")
        with open(path, 'w') as f:
            f.write('')
        return ''
    except PermissionError:
        # 失敗させず、代替手段を提供する
        print(f"Cannot access {path}, using default")
        return ''
```

**悪い例: agentに丸投げする**:

```python  theme={null}
def process_file(path):
    # 失敗させて、agentに何とかさせる
    return open(path).read()
```

設定パラメータも、「voodoo constants」(Ousterhoutの法則)を避けるために、根拠を示して文書化すべきだ。適切な値が分からないなら、agentはどうやってそれを決めるのか。

**良い例: 自己文書化**:

```python  theme={null}
# HTTPリクエストは通常30秒以内に完了する
# 遅い接続を考慮して、長めのタイムアウトにしている
REQUEST_TIMEOUT = 30

# 3回のリトライは、信頼性と速度のバランスが取れる
# 断続的な失敗の大半は、2回目のリトライまでに解消する
MAX_RETRIES = 3
```

**悪い例: マジックナンバー**:

```python  theme={null}
TIMEOUT = 47  # なぜ47なのか
RETRIES = 5   # なぜ5なのか
```

### ユーティリティscriptを用意する

agentがscriptを書けるとしても、事前に用意したscriptには利点がある。

**ユーティリティscriptの利点**:

* 生成されたcodeより信頼できる
* tokenを節約できる(codeをcontextに含める必要がない)
* 時間を節約できる(code生成が不要)
* 使用のたびに一貫性を保てる

<img src="https://mintcdn.com/anthropic-claude-docs/4Bny2bjzuGBK7o00/images/agent-skills-executable-scripts.png?fit=max&auto=format&n=4Bny2bjzuGBK7o00&q=85&s=4bbc45f2c2e0bee9f2f0d5da669bad00" alt="指示ファイルと並べて実行可能なscriptを同梱する" data-og-width="2048" width="2048" data-og-height="1154" height="1154" data-path="images/agent-skills-executable-scripts.png" data-optimize="true" data-opv="3" srcset="https://mintcdn.com/anthropic-claude-docs/4Bny2bjzuGBK7o00/images/agent-skills-executable-scripts.png?w=280&fit=max&auto=format&n=4Bny2bjzuGBK7o00&q=85&s=9a04e6535a8467bfeea492e517de389f 280w, https://mintcdn.com/anthropic-claude-docs/4Bny2bjzuGBK7o00/images/agent-skills-executable-scripts.png?w=560&fit=max&auto=format&n=4Bny2bjzuGBK7o00&q=85&s=e49333ad90141af17c0d7651cca7216b 560w, https://mintcdn.com/anthropic-claude-docs/4Bny2bjzuGBK7o00/images/agent-skills-executable-scripts.png?w=840&fit=max&auto=format&n=4Bny2bjzuGBK7o00&q=85&s=954265a5df52223d6572b6214168c428 840w, https://mintcdn.com/anthropic-claude-docs/4Bny2bjzuGBK7o00/images/agent-skills-executable-scripts.png?w=1100&fit=max&auto=format&n=4Bny2bjzuGBK7o00&q=85&s=2ff7a2d8f2a83ee8af132b29f10150fd 1100w, https://mintcdn.com/anthropic-claude-docs/4Bny2bjzuGBK7o00/images/agent-skills-executable-scripts.png?w=1650&fit=max&auto=format&n=4Bny2bjzuGBK7o00&q=85&s=48ab96245e04077f4d15e9170e081cfb 1650w, https://mintcdn.com/anthropic-claude-docs/4Bny2bjzuGBK7o00/images/agent-skills-executable-scripts.png?w=2500&fit=max&auto=format&n=4Bny2bjzuGBK7o00&q=85&s=0301a6c8b3ee879497cc5b5483177c90 2500w" />

上の図は、実行可能なscriptが指示ファイルと並んでどう機能するかを示している。指示ファイル(forms.md)がscriptを参照し、agentはその内容をcontextにロードせずに実行できる。

**重要な区別**: agentが次のどちらを行うべきかを、指示の中で明確にする。

* **scriptを実行する**(最も一般的): 「`analyze_form.py`を実行してフィールドを抽出する」
* **参考として読む**(複雑なロジックの場合): 「フィールド抽出のアルゴリズムは`analyze_form.py`を参照」

ほとんどのユーティリティscriptでは、より信頼でき効率的なため、実行を推奨する。script実行の仕組みの詳細は、下の[実行環境](#実行環境)の節を参照。

**例**:

````markdown  theme={null}
## ユーティリティscript

**analyze_form.py**: PDFからすべてのフォームフィールドを抽出する

```bash
python scripts/analyze_form.py input.pdf > fields.json
```

出力形式:
```json
{
  "field_name": {"type": "text", "x": 100, "y": 200},
  "signature": {"type": "sig", "x": 150, "y": 500}
}
```

**validate_boxes.py**: 重なり合うバウンディングボックスを確認する

```bash
python scripts/validate_boxes.py fields.json
# 戻り値: "OK"、または競合の一覧
```

**fill_form.py**: フィールドの値をPDFに適用する

```bash
python scripts/fill_form.py input.pdf fields.json output.pdf
```
````

### 視覚的な分析を使う

入力を画像としてレンダリングできる場合は、agentに分析させる。

````markdown  theme={null}
## フォームレイアウトの分析

1. PDFを画像に変換する
   ```bash
   python scripts/pdf_to_images.py form.pdf
   ```

2. 各ページの画像を分析して、フォームフィールドを特定する
3. agentは、フィールドの位置と種類を視覚的に確認できる
````

<Note>
  この例では、`pdf_to_images.py`のscriptを自分で書く必要がある。
</Note>

agentの視覚能力は、レイアウトや構造の理解に役立つ。

### 検証可能な中間出力を作る

agentが複雑で自由度の高いタスクを行うと、間違いを犯すことがある。「計画 - 検証 - 実行」パターンは、agentにまず構造化された形式で計画を作らせ、実行する前にscriptでその計画を検証させることで、エラーを早期に捕捉する。

**例**: スプレッドシートに基づいて、PDF内の50個のフォームフィールドを更新するようagentに依頼する場面を考える。検証がなければ、存在しないフィールドを参照したり、競合する値を作ったり、必須フィールドを見落としたり、更新を誤って適用したりするかもしれない。

**解決策**: 上で示したワークフローのパターン(PDFフォーム入力)を使い、変更を適用する前に検証される中間の`changes.json`ファイルを追加する。ワークフローは、分析 → **計画ファイルを作成** → **計画を検証** → 実行 → 検証、となる。

**このパターンが有効な理由:**

* **エラーを早期に捕捉する**: 変更を適用する前に、検証で問題が見つかる
* **機械的に検証できる**: scriptが客観的な検証を提供する
* **やり直しのきく計画**: agentは、元のファイルに触れずに計画を反復できる
* **デバッグが明確**: エラーメッセージが具体的な問題を指す

**使う場面**: バッチ操作、破壊的な変更、複雑な検証ルール、重大な操作。

**実装のヒント**: 検証scriptは、"Field 'signature\_date' not found. Available fields: customer\_name, order\_total, signature\_date\_signed"のように、具体的なエラーメッセージを出す詳細な出力にして、agentが問題を修正しやすくする。

### 依存パッケージ

Skillは、プラットフォーム固有の制限があるcode実行環境で動作する。

* **claude.ai**: npmやPyPIからパッケージをインストールでき、GitHubリポジトリから取得できる
* **Anthropic API**: ネットワークアクセスがなく、実行時のパッケージインストールもできない

必要なパッケージはSKILL.mdに列挙し、[code execution toolのドキュメント](https://platform.claude.com/docs/en/agents-and-tools/tool-use/code-execution-tool)で利用可能であることを確認する。

### 実行環境

Skillは、ファイルシステムへのアクセス、bashコマンド、code実行の機能を備えたcode実行環境で動作する。このアーキテクチャの概念的な説明は、overviewの[The Skills architecture](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview#the-skills-architecture)を参照。

**作成への影響:**

**agentがSkillにアクセスする方法:**

1. **metadataの事前ロード**: 起動時に、全SkillのYAML frontmatterにあるnameとdescriptionがsystem promptにロードされる
2. **ファイルのオンデマンド読み込み**: agentは、必要なときにファイル読み込みtoolを使って、ファイルシステムからSKILL.mdや他のファイルにアクセスする
3. **scriptの効率的な実行**: ユーティリティscriptは、全内容をcontextにロードせずにbash経由で実行できる。tokenを消費するのは、scriptの出力だけだ
4. **大きなファイルによるcontextへのペナルティなし**: 参照ファイル、データ、ドキュメントは、実際に読まれるまでcontext tokenを消費しない

* **ファイルパスが重要**: agentは、Skillのディレクトリをファイルシステムのようにナビゲートする。バックスラッシュではなく、スラッシュ(`reference/guide.md`)を使う
* **ファイルには内容が分かる名前を付ける**: `doc2.md`ではなく、`form_validation_rules.md`のように内容を示す名前を使う
* **発見しやすいように整理する**: ディレクトリは、ドメインや機能ごとに構成する
  * 良い: `reference/finance.md`, `reference/sales.md`
  * 悪い: `docs/file1.md`, `docs/file2.md`
* **包括的なリソースを同梱する**: 完全なAPIドキュメント、豊富な例、大きなデータセットを含める。アクセスされるまでcontextへのペナルティはない
* **決定的な操作にはscriptを優先する**: agentに検証codeを生成させるのではなく、`validate_form.py`を書く
* **実行の意図を明確にする**:
  * 「`analyze_form.py`を実行してフィールドを抽出する」(実行)
  * 「抽出アルゴリズムは`analyze_form.py`を参照」(参考として読む)
* **ファイルアクセスのパターンをテストする**: 実際のリクエストでテストして、agentがディレクトリ構造をナビゲートできることを確認する

**例:**

```
bigquery-skill/
├── SKILL.md (概要、参照ファイルへの案内)
└── reference/
    ├── finance.md (収益の指標)
    ├── sales.md (パイプラインのデータ)
    └── product.md (利用状況の分析)
```

ユーザーが収益について尋ねると、agentはSKILL.mdを読み、`reference/finance.md`への参照を見つけ、bashを呼び出してそのファイルだけを読む。sales.mdとproduct.mdはファイルシステム上に残り、必要になるまでcontext tokenを一切消費しない。このファイルシステムベースのモデルが、段階的開示を可能にしている。agentは、各タスクが必要とするものだけを選んでロードできる。

技術的なアーキテクチャの詳細は、Skills overviewの[How Skills work](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview#how-skills-work)を参照。

### MCP toolの参照

SkillでMCP(Model Context Protocol)のtoolを使う場合は、「tool not found」エラーを避けるため、必ず完全修飾のtool名を使う。

**形式**: `ServerName:tool_name`

**例**:

```markdown  theme={null}
BigQuery:bigquery_schemaのtoolを使って、テーブルスキーマを取得する。
GitHub:create_issueのtoolを使って、issueを作成する。
```

ここで次の意味になる。

* `BigQuery`と`GitHub`は、MCPサーバ名
* `bigquery_schema`と`create_issue`は、それらのサーバ内のtool名

サーバのprefixがないと、特に複数のMCPサーバが利用可能な場合に、agentがtoolを見つけられないことがある。

### toolがインストール済みだと仮定しない

パッケージが利用可能だと仮定しない。

````markdown  theme={null}
**悪い例: インストール済みだと仮定している**:
"pdfライブラリを使ってファイルを処理する。"

**良い例: 依存関係を明示している**:
"必要なパッケージをインストールする: `pip install pypdf`

その後、次のように使う。
```python
from pypdf import PdfReader
reader = PdfReader("file.pdf")
```"
````

## 技術的な注記

### YAML frontmatterの要件

SKILL.mdのfrontmatterには、`name`(最大64文字)と`description`(最大1024文字)のフィールドが必要だ。構造の詳細は、[Skills overview](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview#skill-structure)を参照。

### tokenの予算

最適なパフォーマンスのため、SKILL.mdの本文は500行未満に保つ。これを超える場合は、前述の段階的開示のパターンを使って、別ファイルに分割する。アーキテクチャの詳細は、[Skills overview](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview#how-skills-work)を参照。

## 効果的なSkillのチェックリスト

Skillを共有する前に、次を確認する。

### 基本的な品質

* [ ] descriptionが具体的で、キーワードを含んでいる
* [ ] descriptionに、Skillが何をするかと、いつ使うかの両方が含まれている
* [ ] SKILL.mdの本文が500行未満である
* [ ] 追加の詳細が別ファイルにある(必要な場合)
* [ ] 時間依存の情報がない(または「旧パターン」の節にある)
* [ ] 全体を通して用語が一貫している
* [ ] 例が抽象的ではなく具体的である
* [ ] ファイルの参照が1階層である
* [ ] 段階的開示が適切に使われている
* [ ] ワークフローのステップが明確である

### codeとscript

* [ ] scriptが問題を解決し、agentに丸投げしていない
* [ ] エラー処理が明示的で、役に立つ
* [ ] 「voodoo constants」がない(すべての値に根拠がある)
* [ ] 必要なパッケージが指示に列挙され、利用可能であることが確認されている
* [ ] scriptに明確なドキュメントがある
* [ ] Windows形式のパスがない(すべてスラッシュ)
* [ ] 重要な操作に、検証・確認のステップがある
* [ ] 品質が重要なタスクに、フィードバックループが含まれている

### テスト

* [ ] 少なくとも3つの評価を作成した
* [ ] Haiku、Sonnet、Opusでテストした
* [ ] 実際の使用シナリオでテストした
* [ ] チームのフィードバックを取り入れた(該当する場合)

## 次のステップ

<CardGroup cols={2}>
  <Card title="Agent Skillsを始める" icon="rocket" href="https://platform.claude.com/docs/en/agents-and-tools/agent-skills/quickstart">
    最初のSkillを作成する
  </Card>

  <Card title="Claude CodeでSkillを使う" icon="terminal" href="https://code.claude.com/docs/en/skills">
    Claude CodeでSkillを作成・管理する
  </Card>

  <Card title="APIでSkillを使う" icon="code" href="https://platform.claude.com/docs/en/build-with-claude/skills-guide">
    Skillをプログラムからアップロードして使う
  </Card>
</CardGroup>
