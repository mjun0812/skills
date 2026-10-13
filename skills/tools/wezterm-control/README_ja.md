# wezterm-control

[English](README.md)

weztermのpane・tab・windowを`wezterm cli`で操作する。paneの分割・フォーカス移動・リサイズ・zoom・close、tab/windowの作成・切替・リネーム、paneの表示内容の読み取り、paneへのコマンド送信と実行結果の確認を行う。

weztermと明示して依頼したときだけ使う。tmuxやHerdrの操作、weztermと明示されていないpane/tab操作の依頼、wezterm自体の設定(`wezterm.lua`やkeybinding)の変更には使わない。

## 使い方

- 「weztermのpaneを分割して」
- 「weztermの別paneでコマンドを実行して」

```text
weztermのpaneを右に分割して
weztermの隣のpaneで make build を実行して
```

## 動作

- 毎回、最初に`wezterm cli list --format json`でwindow・tab・paneの構成を取得する。失敗する場合(`wezterm`が無い、weztermが起動していない、mux serverに接続できない)は、その旨を報告して終了する。
- すべてのコマンドで`--pane-id`または`--tab-id`を明示する。ID省略時は自分が動いているpane(`WEZTERM_PANE`)が対象になるため。「隣のpane」のような相対指定は`get-pane-direction`で解決する。
- 依頼された操作だけを行う。依頼されていないpaneのclose、フォーカス移動、レイアウト変更はしない。
- 他のpaneへ確認なしで送るのは非破壊なコマンドのみ。削除・強制終了・push・デプロイなどは事前に確認する。`kill-pane`の対象は、そのセッションで作成したpaneに限り、それ以外は確認を取る。
- `split-pane`と`spawn`はフォーカスを新しいpaneへ移すため、移動を求められていない限り、完了後に元のpaneへフォーカスを戻す。
- コマンドは`send-text --no-paste`で末尾に改行を付けて送る。付けないとペーストされるだけで実行されない。
- 結果は`get-text`で読み取り、負の`--start-line`でscrollbackを遡る。alternate screenを使うプログラム(TUI、coding agent)の出力はscrollbackに残らないため、そのプログラムにファイルへ書かせて読む。
- 長時間コマンドの完了は、終了コードを出力するmarker(例: `__WEZTERM_DONE_0__`)を末尾に付けて送り、`get-text`をpollingして検知する。
- 最終報告には、実行した操作、作成・操作したpane-id/tab-id、コマンド送信時は`get-text`による検証結果を含める。

## 依存

- `wezterm` CLI(実機確認済みのsubcommandは[references/cli_reference.md](references/cli_reference.md)にある)

手順の詳細は[SKILL.md](SKILL.md)を参照。
