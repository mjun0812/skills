# github-fix-ci

[English](README.md)

PR(またはcurrent branch)のCIステータスを確認し、失敗したログを取得してエラーを分類(テスト、lint、ビルド、型、その他)し、修正してcommit・pushするSkill。PRのhead commitに一致するworkflow runだけを対象にするため、古いrunを根拠に修正することはない。

コンフリクト、CI、レビューコメントをまとめて直すには、本skillを呼ぶ[`github-pr-fix`](../github-pr-fix/README_ja.md)を使う。

## 使い方

- 「CIを直して」
- 「CIが落ちているので修正して」

```text
/github-fix-ci
/github-fix-ci 123 --dry-run
/github-fix-ci --no-commit
```

## 引数

| 引数          | 効果                                                                       |
| ------------- | -------------------------------------------------------------------------- |
| `PR number`   | 確認するPR。省略時は現在のbranchのPR。PRが無ければrepositoryモードで動く。 |
| `--no-commit` | ファイルは修正するが、commitとpushはスキップする。                         |
| `--dry-run`   | 失敗分析と修正方針の提示で終了する。ファイル編集、commit、pushは行わない。 |

## 動作

- PR番号が指定された場合、または現在のbranchにPRが紐づく場合はPRモードで動く。PRが無ければrepositoryモードになり、commitとpushは行わず、ユーザーが手動でcommitするよう案内する。
- PRモードのcommit messageはPRの言語(曖昧なら英語)に合わせる。`fix: resolve CI failures - <description>`または`fix: CI失敗を修正 - <説明>`。
- すべてのcheckが成功していれば成功を報告して終了する。実行中のcheckがある場合は、待機せずステータスを報告して終了する。
- 失敗ログは、`headSha`がPR headと一致するrunの`gh run view --log-failed`から取得する。runが複数残る場合は、失敗したcheck名に対応するrunを優先し、曖昧なら最新のrunだけを使う。
- 複数の失敗は依存関係の順(例: ビルド、テスト)に修正する。stageするのは修正したファイルだけ。
- 修正が不明確またはリスクがある場合はユーザーに確認する。flakyと思われるテストや環境起因の失敗(secretの不足、権限など)は手動対応として報告し、同じCIが繰り返し失敗する場合は根本原因の調査を提案する。
- push後は、CIが再実行されることを伝え、完了後の再確認を提案する。

## 依存

- `git`と`gh` CLI

手順の詳細は[SKILL.md](SKILL.md)を参照。
