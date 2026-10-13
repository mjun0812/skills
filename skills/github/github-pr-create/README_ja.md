# github-pr-create

[English](README.md)

現在のbranchをpushしてPull Requestを作成する。タイトルと本文は、base branchとの差分とcommitから生成する。本文は概要と背景、関連Issue、実装方針、変更内容、影響、検証結果で構成する。labelはrepositoryの既存labelから選び、assigneeは常に`@me`にする。

Issueの起票や磨き上げには[`github-issue-create`](../github-issue-create/README_ja.md)を使う。Issueの実装からPR作成までを一気通貫で行うには、最後に本skillを呼ぶ[`github-issue-resolve`](../github-issue-resolve/README_ja.md)を使う。

## 使い方

- 「PR作って」
- 「pull request作成して」

```text
/github-pr-create
/github-pr-create --dry-run
/github-pr-create language=ja
```

## 引数

| 引数        | 効果                                                                                                                  |
| ----------- | --------------------------------------------------------------------------------------------------------------------- |
| `language`  | PRのタイトルと本文の言語(`ja`、`en`)。省略時はrepositoryのPR templateの言語、templateが無ければ会話の言語に従う。     |
| `spec`      | `Closes`の最優先候補として扱うIssue番号。呼び出し元のskillから渡される。                                              |
| `--dry-run` | 生成したタイトル、本文、base/head、図・画像の成果物を提示する。push、添付のアップロード、`gh pr create`は実行しない。 |

## 動作

- default branchにいる場合や未commitの変更がある場合は、branch名とcommitの分割案を提示し、承認後にbranch作成とcommitを`git-commit`へ委譲する。
- base branchは、会話でユーザーが明示したものを使い、無ければdefault branchを使う。無関係なcommitが含まれる場合は、HEADが積み上がっているopen PRのhead branchを選ぶか、ユーザーに確認する。選んだbase、その理由、commit一覧を報告するため、誤った選定に気付ける。
- 現在のbranchのPRが既にある場合は、URLと状態を表示して中止する。
- repositoryのPR templateがあれば見出しと順序をそのまま使い、無ければ`references/pr_template.md`または`pr_template_ja.md`を使う。書くことが無い項目は削除せず`該当なし`と明記する。
- 本文はcommit一覧とdiffを根拠に書く。推測で事実を補わず、public repositoryへ投稿するときはprivate repositoryの情報を書かない。
- 文章だけでは伝わりにくい箇所は、`references/visuals.md`に従い、表、`diff`やtreeのコードブロック、Mermaid、画像を加える。
- pushは通常のpushを使い、`--force-with-lease`はユーザーに確認した場合だけ使う。
- 本文は`--body-file`で`gh pr create`へ渡す。結果として、PRのURL、タイトル、base/head、関連Issue、label、変更規模を表示する。

## 依存

- branch作成とcommitのための[`git-commit`](../../git/git-commit/README_ja.md)
- `git`と`gh` CLI

手順の詳細は[SKILL.md](SKILL.md)を参照。
