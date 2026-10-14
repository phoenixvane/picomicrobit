# Pico 2 W から micro:bit V2 の LED を操作

Pico 2 W を BLE セントラル、micro:bit V2 を BLE ペリフェラルとして接続し、micro:bit の 5×5 LED を操作します。インターネットや Wi-Fi は実行時には不要です。

## 1. micro:bit V2 の準備

1. [MakeCode](https://makecode.microbit.org/) で新しいプロジェクトを作成します。
2. 「拡張機能」から `bluetooth` を追加します。`radio` と競合すると表示されたら `radio` を削除します。
3. プロジェクト設定の Bluetooth のペアリング方式を **No Pairing Required（ペアリング不要）** に設定します。このサンプルは暗号化・ペアリングを使用せず、近くの機器から接続できる設定です。
4. JavaScript エディターに [microbit/main.ts](microbit/main.ts) を貼り付けます。
5. ダウンロードした HEX ファイルを micro:bit V2 に書き込み、電源を入れます。小さいひし形が表示されたら待機中です。

micro:bit の標準 MicroPython には BLE API がないため、この構成では micro:bit 側に MakeCode を使います。MakeCode シミュレーターでは Bluetooth 接続を検証できません。

## 2. Pico 2 W の準備

1. [公式 MicroPython ダウンロード](https://micropython.org/download/RPI_PICO2_W/)から **Pico 2 W 用**の安定版 UF2 を入手します。BOOTSEL を押しながら USB 接続し、UF2 をコピーします。
2. Thonny などから Pico の REPL に接続します。
3. `aioble` を Pico にインストールします。PC に `mpremote` をインストールして、Thonny の接続を閉じてから実行できます。

   ```sh
   python -m pip install mpremote
   mpremote connect auto mip install aioble
   ```

   複数のボードが接続されている場合は、`auto` の代わりに Pico のシリアルポート（例：`/dev/ttyACM0` または `COM5`）を指定します。PC にネットワーク接続が必要です。Pico 自体を Wi-Fi に接続する必要はありません。

4. [pico/main.py](pico/main.py) を Pico の `main.py` として保存します。PC からのコピー例（リポジトリのルートで実行）：

   ```sh
   mpremote connect auto fs cp pico/main.py :main.py
   mpremote connect auto reset
   ```

## 動作と使い方

Pico 2 W 基板上の **BOOTSEL ボタン**を使います。外付けボタンや GPIO の配線は不要です。MicroPython の `rp2.bootsel_button()` で押下を読み取ります。通常起動して Bluetooth 接続が完了した後に押してください。電源投入時や USB 接続時に押したままにすると、ファームウェア書き込みモードに入ります。

Pico は micro:bit を探して接続し、最初に表示を消灯します。ボタンを押すたびに **全点灯 → ハート → 中央の1点点灯 → 消灯** の順で表示が変わります。50ミリ秒のデバウンス処理があり、長押しでは1回だけ変わります。次の操作にはボタンを一度離してください。接続前の押下は保存されず、接続時に押していた場合も一度離してから押してください。切断すると再接続を試み、再接続後は消灯から始まります。

複数の micro:bit がある場合、REPL に出る `Found:` の名前を確認して、`TARGET_NAME = "micro:bit の実際の広告名"` に変更してください。初期設定は最初に見つかった名前が `micro:bit` で始まる機器に接続します。

`main()` のボタン処理を変更して、次の操作を組み合わせられます。

```python
await display.on()              # 25個すべて点灯
await display.off()             # すべて消灯
await display.heart()           # ハート表示
await display.pixel(0, 0)       # 左上を点灯（既存表示は保持）
await display.pixel(0, 0, False) # 左上を消灯
```

座標は左上が `(0, 0)`、右下が `(4, 4)` です。通信は micro:bit の Bluetooth UART RX 特性への書き込みで、各コマンドの末尾に改行を付けます。

## 実機での確認

micro:bit に小さいひし形が表示され、Pico のログに `Connected. Press BOOTSEL to change the display.` が出た後、表示が消灯することを確認してください。ボタンを押して離す操作を繰り返し、LED が上記の順に変化すること、長押しで表示が連続して変わらないことを確認してください。micro:bit の電源を入れ直し、再接続することも確認できます。

見つからない場合は micro:bit の電源、Bluetooth 拡張、ペアリング不要設定、広告名を確認してください。スマートフォンなどが接続している場合は、その接続を切ってください。`ImportError: no module named aioble` は Pico 側のライブラリ不足です。

クラウド環境には Bluetooth 実機がないため、無線接続と LED 表示は未検証です。
