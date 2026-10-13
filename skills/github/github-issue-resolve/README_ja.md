# github-issue-resolve

[English](README.md)

GitHub issue番号を起点に、調査、専用worktreeでの実装、PR作成までを一気通貫で実行する。レビューとリポジトリ自身の検証コマンドを通過した変更だけを確定し、元の作業ツリーは変更しない。

成果物は、issueを参照する(`Closes #N`)PRである。情報が不足したissueを先に整えるには[`github-issue-polish`](../github-issue-polish/README_ja.md)を、現在のbranchからPRを作るだけなら[`github-pr-create`](../github-pr-create/README_ja.md)を使う。

## 使い方

- 「#N を解決して」
- 「issueから実装してPRまで」

```text
/github-issue-resolve 123
/github-issue-resolve #123 --draft
/github-issue-resolve 123 --dry-run
```

## 引数

| 引数        | 効果                                                   |
| ----------- | ------------------------------------------------------ |
| `issue`     | 解決対象のissue番号(必須)。先頭の`#`は省略可。         |
| `--draft`   | draft PRとして作成する。                               |
| `--dry-run` | 調査と実装方針の提示で停止する。worktreeは作成しない。 |

## 動作

- issueを読み、出力言語を決める(主に日本語なら日本語、それ以外は英語)。closedのissueは中止する。
- 実装方針の判断に必要な情報が欠けている場合は、推測せずに中止し、選択肢または推奨案を添えて具体的に質問する。
- issue本文の`- [ ]`checklistからタスクキューを作る。checklistがない場合は、独立に検証可能な振る舞いが複数あるときだけ分解する。キューは会話内で管理し、issueへ書き戻さない。実装方針とタスク一覧は簡潔に提示するが、確認は取らない。
- 最新のdefault branchから`<type>/<issue-number>-<slug>`のbranchと、`<repo-root>/.tmp/<repo-name>-worktrees/<branch>`のworktreeを作る。
- 1タスクごとに、毎回新規のimplementer SubAgent([templates/implementer-prompt.md](templates/implementer-prompt.md))で実装し、新規のreviewer SubAgent([templates/reviewer-prompt.md](templates/reviewer-prompt.md))で検証する。差し戻しは同一タスクにつき最大2周で、超えたら中止して未解決の指摘を報告する。判定は構造化フィールドとコマンドの実行結果で行い、SubAgentの完了主張は使わない。
- 全タスク後に、リポジトリのtest・lint・buildコマンド(manifest、タスクランナー、CI設定、READMEの順に探す)を実行する。失敗は最大2周差し戻す。コマンドが見つからなければスキップし、報告に含める。
- `git-commit`と`github-pr-create`でcommitとPR作成を行い、PR本文に`Closes #N`があることを確認する。
- issue、branch、PRのURL、diff statを報告する。worktreeとbranchは、中断した場合も含めて削除する。ただしPR作成に失敗した場合は手動修正のため残す。実装中に破壊的なresetは行わず、PRのPhaseまでcommitもpushもしない。

## 依存

- Skill: [`git-commit`](../../git/git-commit/README_ja.md)、[`github-pr-create`](../github-pr-create/README_ja.md)
- `gh`と`git`のCLI

手順の詳細は[SKILL.md](SKILL.md)を参照。
