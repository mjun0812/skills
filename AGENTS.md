# リポジトリガイド

## 概要

このリポジトリは、複数の実行環境とinstall方法で配布するAgent Skillsを管理する。
skill本体、配布用manifest、英日READMEの一覧を常に一致させる。

## ディレクトリ構成

- `skills/<category>/<name>/`: skillの定義。`SKILL.md`、詳細資料、script、templateを含む。
- `agents/`: agentの定義。
- `.claude-plugin/`と`.codex-plugin/`: plugin配布用manifest。
- `scripts/`: このrepoで管理しているskillのためのscript集。layout、manifestの検証、releaseを行う。

## skillの配布方法

以下のツールで配布が可能であることを確認する。ただし、agentsについては配布できるツールが限られているため、この限りではない。

- Claude Code
- Codex plugin
- apm
- npx skills
- gh skill

## skillの追加と変更

- `SKILL.md`は`skills/<category>/<name>/`の深さにだけ配置し、リポジトリ直下には置かない。
- frontmatterの`name`はdirectory名と一致させ、空でない`description`を記載する。
- `allowed-tools`を指定する場合は文字列で記載し、YAMLの配列にしない。
- 手順の中で他のskillを読み込ませる場合は「Skill toolで`<name>`を呼ぶ」と明示する。`disable-model-invocation: true`のskillは呼べないため、ユーザーに実行を依頼させる。
- skillを追加、削除、改名した場合は`.claude-plugin/plugin.json`の`skills`一覧を更新する。
- `.codex-plugin/plugin.json`は`./skills`全体を参照するため、個別skillの追加だけでは変更しない。
- 各skillには`README.md`(英語)と`README_ja.md`(日本語)を置き、引数・動作・依存などskill単位の説明はここに書く。categoryの`README.md`にはskillの使い分けと各skill READMEへのリンクだけを書く。
- skill一覧を変更した場合は`README.md`と`README_ja.md`を同時に更新する。categoryに`README.md`がある場合はそれも更新する。
- 外部素材をもとにしたskillの出典は両READMEへ記載し、`SKILL.md`には追加しない。

## 英日ドキュメント

`<name>_ja.md`がある文書は、日本語版を原本とする。

- 内容の追加・変更はまず`<name>_ja.md`に行い、英語版の`<name>.md`は日本語版からミラーする。
- 英語版だけを変更しない。英語版で見つけた誤りも、日本語版を直してから英語版へ反映する。
- 見出し・節の順序・表・リンク先は両者で揃え、リンク先は各言語版の文書にする。

## 開発

projectで使うtoolは`mise.toml`で管理する。
globalにinstallされたtoolへ依存せず、最初に次を実行する。

```bash
mise install
```

MarkdownとJSONは`oxfmt`、Pythonは`ruff`、shell scriptは`shellcheck`と`shfmt`でチェックする。

Issue, PRは英語で記述する。

## 検証

変更後は全hookを実行する。

```bash
mise exec -- prek run --all-files --show-diff-on-failure
```

skillまたはplugin manifestを変更した場合は、layoutとmanifestの対応も個別に確認できる。

```bash
mise exec -- python scripts/check_layout.py
mise exec -- python scripts/check_plugin_manifest.py
```

Claude Codeのstrict validationは全hookに含まれる。個別に実行する場合は次を使う。

```bash
mise exec -- claude plugin validate . --strict
```

## Gitとrelease

- versionとtagはSemantic Versioningに従い、tagには`v` prefixを付ける。
- releaseはcleanなworktreeで`mise run release <version>`を実行する。
- release taskはmanifestのversion更新、commit、tag、pushまで行うため、明示的なrelease依頼がある場合だけ実行する。
