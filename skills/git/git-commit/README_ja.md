# git-commit

[English](README.md)

stage済みとunstagedの変更を読み取り、内容を要約したConventional Commits形式のメッセージを生成してcommitする。stageされた変更が無ければ現在の変更をstageしてからcommitする。pushは行わない。

メッセージは指定した言語(デフォルトは英語)で記述する。出力は生成したcommitメッセージのみ。

## 使い方

- `git commit`を実行する際に使う: 「現在の変更を確認して、コミットする」

```text
/git-commit
/git-commit ja
```

## 引数

| 引数       | 効果                                                   |
| ---------- | ------------------------------------------------------ |
| `language` | commitメッセージの言語(`ja`、`en`)。デフォルトは英語。 |

## 動作

- 開始前に`git diff --cached`、`git diff`、`git status`、現在のbranchを取得する。
- stage済み・unstagedの変更がどちらも無い場合は、commit対象が無い旨を報告して終了する。
- すでにstageされた変更がある場合は、それだけをcommitし、追加のstageは行わない。stageされた変更が無い場合は、現在の変更を確認してstageする。
- メッセージの形式は`<type>: <description>`(scopeなし)、空行、1行1変更の箇条書き。規則は[references/conventional_commits.md](references/conventional_commits.md)にある。
- 本文の文体は言語に従う。日本語は体言止めで終え、ですます調は使わない。英語は`- Add retry on login failure`のような命令形の断片で書く。
- commit完了後、生成したメッセージのみを出力する。
- 許可するtoolは`git status`、`add`、`branch`、`diff`、`commit`に限る。

手順の詳細は[SKILL.md](SKILL.md)を参照。
