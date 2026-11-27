---
name: github-pr-fix
description: PRの全問題(コンフリクト、CI失敗、レビューコメント)を自動検出してgit worktree内で修正するSkill。ユーザーが「PRの問題を全部直して」「PRをまとめて修正して」「レビューコメントが来たので対応して」「レビューが返ってきたので修正して」のように依頼したら使うこと。コンフリクト解消だけ、CI修正だけの依頼には使わない。
allowed-tools: Skill, Bash(git:*), Bash(gh:*), Bash(cat:*), Bash(ls:*), Bash(bat:*), Bash(eza:*), Bash(grep:*), Bash(head:*), Bash(tail:*), Bash(jq:*), Bash(bash:*)
---

# GitHub PR Fix

指定されたPRをmerge可能な状態へ戻すために、コンフリクト・CI失敗・未対応レビューコメントを検出し、該当するものだけを解消してPR head branchへ反映するSkill。
修正作業はPRごとの専用Git worktree内で行い、修正内容はPRの言語に合わせて生成し、ユーザーへの報告も同じ言語で行う。
**3つのサブSkillを正しい順序でオーケストレーションし、検出された問題に対応するSkillだけを呼び出す**。

- `git-fix-conflict`: コンフリクトの解消
- `github-fix-ci`: CI失敗の修正
- `github-resolve-pr-comment`: レビューコメントへの対応

修正・commit・pushは必ず専用worktree内で行う。Skillを起動した元の作業ツリーでは、PR情報の取得とworktree作成以外のファイル編集・commit・pushを行わない。

## Arguments

- `PR number` (Optional): 修正するPR番号。省略時は現在のブランチに紐づくPRを対象とする

## Task

### Phase 1: 事前チェック

1. 対象PRの特定:
   - 引数でPR番号が指定されている場合はそのPRを使用する
   - 引数が指定されていなければ、現在のブランチに紐づくPRを使用する
   - PRが存在しない場合はエラーメッセージを表示して中止
2. `owner/repo` を取得: `gh repo view --json owner,name --jq '"\(.owner.login)/\(.name)"'`
3. PRの `baseRefName` / `headRefName` / `headRepositoryOwner` / `isCrossRepository` を取得する
4. cross repository PRの場合は、現在の認証ユーザーがhead repositoryへpushできるかを確認する。pushできない場合は、修正内容を作れてもPRへ直接反映できないため中止して理由を報告する
5. push先 `<push-remote>` を決定する。PR head branchはhead repositoryにあるため、cross repository PRで `origin` (base repository) へpushしないこと:
   - 同一リポジトリのPR: `origin`
   - cross repository PR: head repositoryのURL。`origin` のURL形式に合わせて `https://github.com/<head-repository-owner>/<head-repo-name>.git` または `git@github.com:<head-repository-owner>/<head-repo-name>.git` を組み立てる
6. PRのタイトルと本文から言語を検出する (例: 日本語、英語)。曖昧な場合は英語をデフォルトとする。検出はここで1回だけ行い、すべての報告とサマリーをこの言語で記述し、Phase 4の引き継ぎ制約に含めてサブSkillへ渡す (サブSkillに独立して再検出させない)
7. 最終サマリー用テンプレートを検出された言語に応じて決定する:
   - English/default: [`references/summary_template.md`](references/summary_template.md)
   - Japanese: [`references/summary_template_ja.md`](references/summary_template_ja.md)

### Phase 2: 修正用worktreeの作成

1. `<repo-root>/.tmp/<repo-name>-worktrees/pr-<number>-fix` を専用worktree pathとする。
2. 同じpathのworktreeまたはlocal branch `pr-fix/<number>` が既に存在する場合は、cleanでも作り直さず中止し、既存のパスとbranch名を報告する。
3. PR headとbase branchをfetchする: `git fetch origin +pull/<number>/head:refs/pr-fix/<number>/head` および `git fetch origin +<base-ref-name>:refs/pr-fix/<number>/base`
4. `git worktree add -b pr-fix/<number> <worktree-path> refs/pr-fix/<number>/head` で、`headRefName` ではなくfetch済みのrefから専用local branchを作ってcheckoutする。`headRefName` はPR head branch名としてpush先の判定に使う。checkout対象にはしない。fork PRや同名branchの衝突で別branchを修正しないよう、worktreeの `HEAD` が `refs/pr-fix/<number>/head` のcommit SHAと一致することを確認する。今回作成したworktree、branch、一時refを記録する。
5. Phase 3以降は、すべての操作を `<worktree-path>` 配下で実行する。

### Phase 3: 問題の検出

3種類の問題を並列に検出し、検出結果に応じてPhase 4で必要なSkillだけ呼び出す。
検出は `<worktree-path>` をcwdとし、PR番号を明示して実行する。

- **1. コンフリクト**: `mergeable` が `CONFLICTING` の場合のみ対応する。`MERGEABLE` / `UNKNOWN` はスキップする。
- **2. CI失敗**: `FAILURE` / `CANCELLED` / `TIMED_OUT` のcheckがある場合のみ対応する。全て実行中の場合はステータスを報告し、Phase 4のStep 2はスキップする。
- **3. 未対応レビューコメント**: 次のどちらかに該当する場合のみ対応する。
  - inline review threadのunresolved数が1件以上ある。unresolved数は[`scripts/fetch_review_threads.sh`](scripts/fetch_review_threads.sh)の`--only-unresolved`で取得し、review全体のstateだけでは判定しない(stateベースの判定はunresolved threadを取りこぼす)。
  - 認証ユーザー以外が投稿したreview summary body(`APPROVED`以外で本文があるもの)またはPR-level issue commentのうち、未対応のものが1件以上ある。`gh pr view <number> --json reviews,comments`で取得する。これらにはネイティブな解決機構がないため、依頼や質問を含み、投稿より後のcommitや認証ユーザーのコメントで対応されていないものを未対応と判断する。

### Phase 4: 検出した問題への対応

検出された問題に対して、以下の順序でサブSkillを呼び出す。**前のステップが失敗しても後続のステップは試みる**。大きな変更の前にはユーザーに確認を求める。
各サブSkillは必ず `<worktree-path>` をcwdとして実行する。サブSkillへの引き継ぎには次の制約を明示する:

- PR番号: `<number>`
- 作業ディレクトリ: `<worktree-path>`
- 修正対象branch: `<head-ref-name>`
- base branch: `<base-ref-name>`
- 出力言語: Phase 1で検出した言語 (リプライ・commit message・報告に使用する)
- worktree外のファイルを編集しない
- commit / pushは `<worktree-path>` 内のPR head branchから行う
- push時は必ず `git push <push-remote> HEAD:<head-ref-name>` の形式でPR head branchへ明示的に反映すること (worktreeのlocal branch名は`pr-fix/<number>`でありPR head branch名と異なるため。`<push-remote>` はPhase 1で決定したもの)

#### Step 1: コンフリクトの解消

Phase 3でコンフリクト (`CONFLICTING`) が検出された場合のみ:

- `<worktree-path>` 内でSkill toolで `git-fix-conflict` を呼ぶ
- 完了を待ってから、再度 `gh pr view --json mergeable --jq '.mergeable'` でコンフリクトが解消されたことを確認する
- 検出された言語でステータスを報告する

#### Step 2: CI失敗の修正

Phase 3で失敗チェックが検出された場合のみ:

- `<worktree-path>` 内でSkill toolで `github-fix-ci` を呼ぶ
- 完了を待つ。プッシュ後にCIが再実行されることに注意する
- 検出された言語でステータスを報告する

#### Step 3: レビューコメントへの対応

Phase 3で未対応レビューコメントが検出された場合のみ、次を行う。

- `<worktree-path>` 内でSkill toolで `github-resolve-pr-comment` を呼ぶ (同Skillにはレビューコメントへのリプライを常に投稿させる)
- 完了後、再度 [`scripts/fetch_review_threads.sh`](scripts/fetch_review_threads.sh) の `--only-unresolved` でunresolved数の差分を取って報告する
- 検出された言語でステータスを報告する

### Phase 5: 最終確認

1. `<worktree-path>` 内で未commit変更と直近のcommitを確認し、`gh pr view <number> --json url,mergeable,mergeStateStatus` と `gh pr checks <number>` でPRの最終状態を確認する
2. commit済みだが未pushの変更が残っている場合は、`<worktree-path>` 内から `git push <push-remote> HEAD:<head-ref-name>` でPR head branchへpushする
3. 未commit変更が残っている場合は、対象サブSkillの失敗として扱い、内容を検出された言語で報告する

### Phase 6: 最終サマリー

Phase 1で決定したテンプレートを使い、最終出力として表示する。

- 「対応内容」には、Phase 3で検出した問題の行だけを載せる
- その下に、Phase 4で呼び出した各サブSkillが返した報告の全文を、呼び出した順に載せる

### Phase 7: クリーンアップ

対象は今回の実行で作成したworktreeとbranchだけにする。途中のエラー、ユーザーの中止、未commit変更、未pushのcommitがある場合は削除せず、残したパス、branch名、理由を報告する。

1. 正常完了した場合だけ、`git -C <worktree-path> status --porcelain` が空であることを確認する。local HEADと最新PR headのSHAを取得し、`git merge-base --is-ancestor <local-head-sha> <latest-pr-head-sha>` を実行する。local HEADが最新PR headの祖先であることを確かめる向きであり、終了コード0の場合だけ削除へ進む。確認失敗や未反映のcommitがあればworktreeとbranchを残す。
2. worktree外をcwdにして、ネイティブの `git worktree remove <worktree-path>` を独立した操作として実行する。`--force` を付けない。
3. worktree削除が成功した場合だけ `git branch -d pr-fix/<number>` を実行し、今回作成した一時refを削除する: `git update-ref -d refs/pr-fix/<number>/head` および `git update-ref -d refs/pr-fix/<number>/base`。branch削除が拒否された場合はbranchを残す。
4. 削除の失敗や承認拒否はそのまま報告し、残したパスとbranch名を示す。force、reset、clean、再帰削除、wrapperへの置換で拒否を迂回しない。親ディレクトリや他のworktreeを掃除しない。
