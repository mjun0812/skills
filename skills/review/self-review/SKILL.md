---
name: self-review
description: 自分で書いた変更 (現在のbranchの変更と未commit変更、または指定した1 commit) を敵対的にコードレビューし、検証を通過した指摘だけをチャットへ返すSkill。PRの作成前後に自己採点として使い、GitHubへは投稿しない。ユーザーが「自分の変更を厳しくレビューして」「PRを出す前にself reviewして」「このcommitをself reviewして」のように依頼したら使うこと。
---

# Self Review

自分のbranchの変更または指定commitを一時worktreeへ固定し、ユーザーのworking treeを変更せずにレビューする。
Finderが出した候補を、1件ずつVerifierが実コードを実行して確かめる。再現できた指摘を要修正として、再現はできないが反証も無い指摘を未証明として、localへ出力する。
変更目的や作者の想定を未検証の仮説として扱い、変更を壊す入力・状態・実行順序を積極的に探す。厳しさは探索範囲と反証の深さに使い、指摘の証拠基準は下げない。
PRがあってもレビューやcommentは投稿しない。GitHubからはPRのタイトル、本文、base branchを読むだけとする。

## Arguments

- `commit`: reviewするcommit-ish。指定時は対象を提案せず、そのcommitだけをレビューする
- `--base <ref>`: branchの変更の起点にするref。指定時は対象を提案せず、このbaseからのbranchの変更をレビューする。省略時は現在のbranchのopen PRのbase branch、PRが無ければ`gh`が解決するrepositoryのdefault branchを使う。`commit`指定時は使わない

## 対象

レビュー対象は次の3種類で、branchの変更を基本とする。`commit`と`--base`のどちらも指定されなければ、Phase 1で候補を集計してユーザーに提案する。

| 対象             | baseline               | 含む変更                                                                           |
| ---------------- | ---------------------- | ---------------------------------------------------------------------------------- |
| branchの変更     | baseとHEADのmerge-base | baselineからHEADまでのcommit、staged・unstaged・untracked (`.gitignore`対象外のみ) |
| 未commit変更のみ | HEAD                   | staged・unstaged・untracked                                                        |
| 1 commit         | commitのfirst parent   | そのcommitが導入した差分だけ。現在の未commit変更は含めない                         |

branchの変更は、PRの作成前と作成後のどちらでも、PRに載る変更とまだcommitしていない変更をまとめてレビューできる。first parentがないroot commitと、checkoutしていない他のbranchやPRは対象外とする。

## Workflow

### Phase 1: 対象の決定とsnapshotの作成

1. 現在位置からrepository rootを特定する。Git repositoryでなければ終了する。
2. `commit`指定時は手順4へ進む。それ以外は`scripts/self_review_target.sh`でbase、現在のbranchのopen PR、候補ごとの変更量を集計する。`--base`を指定された場合はそのまま渡す。scriptはbaseを指定されなければ、PRのbase repository(PRが無ければ`gh`が解決するrepository)を指すremoteからbase branchをfetchし、その`<remote>/<branch>`をbaseとする。fork構成で古い`origin/main`をbaseにしないためである。
   - 標準出力のJSONの`base`をbaseとして保持する
   - 以下のPRの情報は、`--base`を省略したか、PRのbase(`origin/<baseRefName>`のような`base`の値)と同じ値を指定したときだけ使う。別のbaseを指定した範囲はPR全体と一致しないためである
   - `pr`がnullでなければ、手順3で対象がbranchの変更に決まったときだけ、PRのタイトルと本文を`<change-description>`に使う。PR全体の説明を一部の差分の目的として渡すと、対象外の振る舞いに照らした指摘が出るためである
3. `--base`指定時はbranchの変更を対象にする。それ以外は、JSONの`commits`(merge-base以降のcommit数)と`hasUncommitted`から対象を決める。

   | `commits` | `hasUncommitted` | 対象                                                                                           |
   | --------- | ---------------- | ---------------------------------------------------------------------------------------------- |
   | 0         | false            | 対象なしとして終了する                                                                         |
   | 0         | true             | 質問せずに未commit変更のみ                                                                     |
   | 1         | false            | 質問せずにbranchの変更                                                                         |
   | 2以上     | false            | `AskUserQuestion`で「branchの変更(Recommended)」「最新commitのみ」から選ぶ                     |
   | 1以上     | true             | `AskUserQuestion`で「branchの変更(Recommended)」「未commit変更のみ」「最新commitのみ」から選ぶ |

   HEADがmerge commitの場合(`headIsMerge: true`)は「最新commitのみ」を選択肢から外す。merge commitのfirst parentとの差分は、取り込んだ他人の変更になるためである。外した結果、選択肢がbranchの変更だけになった場合は質問せずにbranchの変更を対象にする。

   選択肢の説明には、`stats`の`branch` / `uncommitted` / `head`の変更量を書く。branchの変更にはcommit数とPR番号(PRがあれば)を、branchの変更と未commit変更のみには`untrackedFiles`が1以上ならuntracked fileの数を添える。`stats`はuntracked fileを数えていないためである。

4. 対象に応じて`scripts/self_review_snapshot.sh`を実行する。
   - branchの変更: `create-branch --repo <repo-root> --base <base>`で、HEADに未commit変更を重ねたsnapshotを作り、merge-baseとの差分を取得する
   - 未commit変更のみ: `create-branch --repo <repo-root> --base HEAD`で、HEADとの差分を取得する
   - 1 commit: `create-commit --repo <repo-root> --commit <commit>`で、commitをdetached worktreeへ展開し、first parentとの差分を取得する。最新commitのみを選んだ場合は`<commit>`を`HEAD`とする
5. 標準出力で返された`metadata.json`を読み、次を保持する。
   - `mode` (`branch`または`commit`。未commit変更のみもbranch modeになる)
   - `repoRoot`
   - `worktree`
   - `baseRef`
   - `baselineSha`
   - `headSha`
   - `hasUncommitted`
   - `diffFile`
   - `changedFilesFile`
   - `commitsFile`
6. `diffFile`と`changedFilesFile`を読み、レビュー対象差分を確定する。branch modeではsnapshot内の変更がindexへstagingされているため、再確認には`git diff --cached <baselineSha>`を使用する。commit modeでは`git diff <baselineSha> <headSha>`を使用する。

```bash
bash "<skill-dir>/scripts/self_review_target.sh" --repo "<repo-root>" [--base "<base>"]
metadata_path=$(bash "<skill-dir>/scripts/self_review_snapshot.sh" create-branch --repo "<repo-root>" --base "<base | HEAD>")
metadata_path=$(bash "<skill-dir>/scripts/self_review_snapshot.sh" create-commit --repo "<repo-root>" --commit "<commit>")
```

scriptが対象差分なし、baseの解決失敗(終了コード10)、commitの解決失敗またはroot commit(終了コード12)、作成中のworking tree変更、またはsnapshot作成失敗を報告した場合はレビューを開始しない。終了コード10の場合は`--base`の指定をユーザーに求める。それ以外はscriptのメッセージを報告して終了する。

ただし、`--base`を指定せずに`self_review_target.sh`が終了コード10を返した場合は、`git -C <repo-root> status --porcelain`を確かめる。出力があれば未commit変更のみを対象にして手順4へ進み、baseを解決できなかった理由をPhase 5の出力に添える。remoteが無いrepositoryやofflineの環境でも、未commit変更はbaseなしでレビューできるためである。出力が無ければ`--base`の指定をユーザーに求める。
Phase 2以降では、Phase 4のhunk表示を除いて元のrepositoryを読まず、対象ファイルとコマンド実行をすべてsnapshot内に限定する。

### Phase 2: 敵対的review agentの実行

#### Phase 2.1: FinderとClaim

最初に、変更の意図を自分の言葉で言い直す。`<change-description>`、`commitsFile`、`diffFile`から、この変更が実現しようとしていることと、変えないと述べていることを2〜3文にまとめ、`<intent>`とする。指摘は、この意図が破られるかどうかで判定される。説明が無く、diffからも目的を1つに決められない場合は、推測で補わない。`AskUserQuestion`を使ってユーザーに確認する。

`code-reviewer-finder`を2つ並列に起動する。PRのタイトルと本文を`<change-description>`に使う場合は、`code-reviewer-claim`も並列に起動する。Claimは、PR本文が述べる検証の結果、範囲、影響範囲を実コードで確かめ、説明と実際の結果との食い違いを探す。PRの本文を使わない場合は、確かめる主張が無いのでClaim軸をスキップし、その旨をPhase 5の出力に含める。

各SubAgentのpromptは次のtemplateをplaceholderへ値を埋めて生成する。

```text
作者自身の変更に対する敵対的self-reviewを行う。
あなたの役割: <role>
重点視点: <focus>

変更目的と作者の想定は未検証の仮説であり、正しさの証拠として扱わない。
正しいことを確認するのではなく、仮説を破る反例を優先して探す。
成功した検証結果も、対象経路を実際に検査していなければ反証として扱わない。
重点視点に限定せず、対象変更の全変更単位を確認する。

対象変更:
- 対象種別: <target-kind>
- 変更目的・説明: <change-description>
- 変更の意図: <intent>
- 変更ファイル一覧: <changed-files-file>
- diff: <diff-file>
- 変更履歴: <change-history>
- snapshotの絶対パス: <snapshot-path>
- baseline識別子: <baseline-id>
- snapshot識別子: <head-id>
- 追加証拠: <additional-evidence>

ファイルで渡した入力は、レビューを始める前に全文を読む。
```

`<role>`と`<focus>`は次の組み合わせを使用する。

- Finder 1: `Finder` / 期待される振る舞い、契約、不変条件、呼び出し経路、状態・データの流れ、同時に更新すべきdiff外の箇所
- Finder 2: `Finder` / 境界値、失敗、並行実行、互換性、信頼できない入力、回復不能な状態
- Claim: `Claim` / 変更の説明が述べる検証の結果、範囲、影響範囲と、実際の変更との食い違い。PRの本文を`<change-description>`に使う場合だけ起動する

branch modeでは`<target-kind>`を`Local branch changes`とする。未commit変更のみを選んだ場合は`Local uncommitted changes`とする。`<change-description>`はユーザー指定の目的、PRのタイトルと本文(対象がbranchの変更の場合のみ)、「`<baseRef>`からの変更」の順に、最初に得られたものとする。`<change-history>`は`commitsFile`のパスとし、`hasUncommitted`がtrueなら「未commit変更を含む」と添える。commit modeでは順に`Local commit`、commit message、`commitsFile`のパスとする。`<baseline-id>`にはmetadataの`baselineSha`を指定する。`<head-id>`には、commit modeでは`headSha`を、branch modeでは「HEAD `<headSha>`に未commit変更を重ねたsnapshotのindex。baselineとの比較にはsnapshot内で`git diff --cached <baselineSha>`を使う」と指定する。branch modeの変更はsnapshotのindexにだけあり、`headSha`と比べると未commit変更が抜けるためである。その他のplaceholderはPhase 1のmetadataと対象差分から埋め、`<changed-files-file>`と`<diff-file>`にはmetadataの`changedFilesFile`と`diffFile`を指定し、`<additional-evidence>`は`なし`とする。

FinderとClaimには、テストや再現コードの実行を許可する。実行は各SubAgentがsnapshotから書き出した実行用コピーで行わせ、snapshotのファイルは変更させない。snapshotの中で実行すると、生成物がPhase 3の有効性確認とPhase 6のcleanupを止めるためである。

起動したSubAgent(専用agentを使えない環境では、同じpromptを渡した汎用SubAgent)のいずれかが起動できない、または結果を返さない場合は、diffを自分で読んで代わりにレビューしない。同時実行数の上限による失敗も同じとする。Phase 6のcleanupを実行し、レビューできなかったことと原因だけを報告して終了する。Phase 2.2〜2.3の`code-reviewer-verifier`も同じとする。

#### Phase 2.2: Finder候補の検証

両Finderの出力を1つの候補集合へまとめ、agent定義の形式を満たし、レビュー対象差分が導入・露出した候補をすべて採用する。作者の意図や見た目の発生確率だけを理由に、Verifierの前で候補を破棄しない。
同じ`filepath:line`または同じ根本原因の候補は、Verifierの起動前に1件へまとめる。

候補1件ごとに`code-reviewer-verifier`を起動し、次のprompt templateを使用する。

```text
次のコードレビュー候補1件を、支持せずに反証を優先して独立検証する。
候補種別: <candidate-type>
検証対象の指摘:
<candidate>

対象変更:
- 対象種別: <target-kind>
- 変更目的・説明: <change-description>
- 変更ファイル一覧: <changed-files-file>
- diff: <diff-file>
- snapshotの絶対パス: <snapshot-path>
- baseline識別子: <baseline-id>
- snapshot識別子: <head-id>
- 追加証拠: <additional-evidence>

ファイルで渡した入力は、検証を始める前に全文を読む。
```

Finder候補では`<candidate-type>`を`Finder`、`<candidate>`を候補全文とする。他のplaceholderはPhase 2.1と同じ値を使用する。

Verifierには、候補の`再現`のコマンド列と、関連する最小のテストや再現コードの実行を許可する。実行は実行用コピーで行わせ、snapshotのファイルは変更させない。
verdictが`confirmed`の候補だけを確定指摘とし、`refuted`と`uncertain`は破棄して、verdictごとの件数を数える。確定指摘は、Verifierの`証明`で2つに分ける。`再現`の指摘は要修正とし、Verifierの`実行結果`のコマンド列と出力を添える。`追跡`の指摘は未証明とする。

#### Phase 2.3: Claim候補の検証

Claimを起動した場合のみ実行する。Claimの出力から、形式(`問題` / `根拠` / `完了条件`)を満たす候補だけを採用する。確定指摘と同じ行または同じ根本原因の候補を破棄した上で、残りを1件ずつ`code-reviewer-verifier`で検証する。
VerifierにはPhase 2.2のprompt templateを使用し、`<candidate-type>`を`Claim`、`<candidate>`を候補全文とする。
verdictが`confirmed`の候補だけを確定指摘とし、`refuted`と`uncertain`は破棄して件数に加える。Claimの出力の`一致`と`未確認`は、主張の件数としてPhase 5の出力に使う。

### Phase 3: snapshotの有効性確認

出力前に`verify`を実行する。branch modeでは元のrepositoryのHEADとworking treeがsnapshot作成時から変化していないことを、両modeではreview用worktreeがagentに変更されていないことを確認する。

```bash
bash "<skill-dir>/scripts/self_review_snapshot.sh" verify --metadata "$metadata_path"
```

一致しない場合はレビュー結果を破棄し、変更後に再レビューが必要なことだけを報告する。古い指摘内容は出力せず、Phase 4も実行しない。

### Phase 4: hunkへの表示

`hunk`があれば、要修正の指摘と未証明の指摘をhunkのnoteとして対象差分の上に表示する。このrepositoryのhunk sessionがあればそれを使い、無ければherdrのpaneでhunkを起動する。どちらもできない環境ではscriptが終了コード3を返すので、このPhaseをスキップしてPhase 5へ進む。

1. 指摘ごとに次のentryを作り、`metadata.json`と同じdirectoryの`hunk-notes.json`へ`{"comments": [...]}`の形で書き出す。指摘が0件なら空の配列にする。古いnoteを消すため、0件でもscriptを実行する。このrepositoryのhunk sessionが無く指摘も0件の場合、scriptはpaneを開かずに終了コード3を返す
   - `filePath`: `path:line`のpath
   - `newLine`: `path:line`のline。`(side=LEFT)`が付いた削除行への指摘では`newLine`を書かず、`oldLine`にlineを書く。renameしたファイルの削除行への指摘では`filePath`に変更前のpathを、追加行への指摘では変更後のpathを使う。`git mv`していない未commitのrenameを、hunkは削除と追加の2ファイルとして表示するためである
   - `summary`: `<Phase 5の連番>. [カテゴリ] 要約`。未証明の指摘は`[カテゴリ]`の前に`[未再現]`を付ける
   - `rationale`: 問題と完了条件を改行で区切った文。Claim由来の指摘では根拠も含める
2. scriptを実行する。scriptは以前のself-reviewが付けたnoteのうち返信が付いていないものを消し、sessionの内容をbranch modeでは`diff <baselineSha>`、commit modeでは`diff <baselineSha> <headSha>`へ切り替えてから、作成者`self-review`としてnoteを付ける。他のagentやユーザーが付けたnoteは消さない

```bash
bash "<skill-dir>/scripts/self_review_hunk.sh" show --metadata "$metadata_path" --notes "<metadata-dir>/hunk-notes.json"
```

標準出力のJSONの`applied`は表示したnoteの件数、`omitted`はdiffのhunk外を指すためhunkに表示できなかった件数、`kept`は返信が付いているため消さずに残した以前のnoteの件数である。終了コード3以外で失敗した場合は、エラーメッセージをPhase 5の出力に添えて続ける。scriptが開いたherdrのpaneは、ユーザーが結果を見るために残し、閉じない。

### Phase 5: local出力

結果はユーザーの言語に合わせ、チャットまたはterminalへ出力する。hunkへ表示した場合も、すべての指摘をチャットへ出力する。ファイルへの保存やGitHubへの投稿は行わない。

- 要修正の指摘が1件以上: `CHANGES_REQUIRED`
- 要修正の指摘が0件: `PASS`。未証明の指摘が何件あっても、Verdictは変えない

冒頭にVerdict、対象範囲、言い直した変更の意図、指摘件数、hunkへの表示結果、レビュワー名と実行中のmodelの名前を記載する。対象範囲はbaseline SHAとhead SHAの先頭7文字で示し、branch modeではbaseのref、PRがあればPR番号、`hasUncommitted`がtrueなら未commit変更を含むことを添える。レビュワー名は実行中のagentの名前で、Claude Codeでは`Claude`と書く。modelの名前は、system promptにある表記をそのまま書く。
指摘は、要修正の指摘、未証明の指摘の順に通しの連番を付け、1つの一覧表に並べる。表の「再現」の列は、要修正の指摘を`✓`、未証明の指摘を`–`にする。指摘が0件なら、表の代わりに`なし`と書く。
表の後に、指摘ごとの詳細を下の形式で連番の順に並べ、項目をすべて埋める。再現には、Verifierが実行したコマンド列と出力を書く。Claim由来の指摘では、`発生経路`の代わりに`根拠`として、説明の該当記述の引用を書く。未証明の指摘では、`再現`の代わりに`再現できなかった理由`として、実行で確かめられなかった理由を書く。
Claim軸をスキップした場合は、件数の代わりにその旨を記載する。起動した場合は、説明の主張のうち実行して一致した件数と、実行できなかった件数を添える。
hunkへの表示をスキップした場合はその理由を、hunk外のため表示できなかった指摘があればその件数を、返信が付いているため残した以前のnoteがあればその件数を記載する。
Verifierが破棄した候補は、`refuted`と`uncertain`の件数だけを記載する。Verifierの検証過程、破棄した候補の内容、内部証拠は出力しない。

````markdown
Verdict: CHANGES_REQUIRED
Range: <baseline-short-sha>..<head-short-sha> (base: <baseRef>, PR #<N>, 未commit変更を含む)
Intent: <言い直した変更の意図>
Findings: 再現 <n>, 未再現 <n>, Claim: 不一致 <n> / 一致 <n> / 未確認 <n> | skipped
Dropped: refuted <n>, uncertain <n>
Hunk: <applied>件を表示, <omitted>件はhunk外, 以前のnote <kept>件を残した | skipped (<理由>)
Reviewer: <レビュワー名> (<model>)

## 指摘事項

| #   | 再現 | 種別     | 場所        | 指摘 |
| --- | :--: | -------- | ----------- | ---- |
| 1   |  ✓   | カテゴリ | `path:line` | 要約 |
| 2   |  –   | カテゴリ | `path:line` | 要約 |

### 指摘1. 要約

`path:line`

<問題>

**完了条件**

- ...

**発生経路**

1. `file:line` (説明)
2. `file:line` (説明)

**再現**

```text
$ <コマンド列>
<出力>
```

### 指摘2. 要約

`path:line`

<問題>

**完了条件**

- ...

**発生経路**

1. `file:line` (説明)

**再現できなかった理由**

...
````

### Phase 6: cleanup

終了、中断、snapshot無効、agent失敗のいずれの場合も、metadataが作成済みなら`cleanup`を実行する。scriptは作成時とHEAD、ファイル内容、indexが一致し、新しいuntracked fileもない場合だけ、初期入力のコピーをsnapshot内でrestoreしてからネイティブの`git worktree remove`で削除する。初期入力以外の変更は捨てない。

```bash
bash "<skill-dir>/scripts/self_review_snapshot.sh" cleanup --metadata "$metadata_path"
```

cleanup対象は今回scriptが作成したworktreeだけとする。変更があった場合や削除に失敗した場合はworktreeを残し、パスと理由を報告する。承認拒否をforce、reset、clean、再帰削除、wrapperへの置換で迂回しない。metadata作成前の失敗では部分的なworktreeを残し、scriptが報告したパスを伝える。親ディレクトリとレビュー資料、他のworktreeは削除しない。元のrepositoryへreset、restore、stash、checkout、cleanを実行しない。hunkのsessionとnote、scriptが開いたherdrのpaneは残す。
