# MEGANE-USAGI
初めてのロボトレース機体

全日本マイクロマウス大会のロボトレース競技に出場するための機体。設計からプログラム、運用までをこのリポジトリで管理する。

## ドキュメント

- [競技規定まとめ](docs/rules.md)
- [攻略方針と技術動向](docs/strategy.md)
- [開発ロードマップ](docs/roadmap.md)
- [上位ロボトレース機体の調査](docs/survey.md)
- [駆動系の検討（1 輪 3 モータ）](docs/design/drive.md)
- [吸引の検討](docs/design/suction.md)
- [電源](docs/design/power.md)
- [モータドライバ](docs/design/motor_driver.md)
- [ラインセンサ](docs/design/line_sensor.md)
- [マイコン](docs/design/mcu.md)
- [エンコーダ](docs/design/encoder.md)
- [重量配分](docs/design/mass.md)
- [仮想ライントレース（最終目標）](docs/design/virtual_line_trace.md)

## ディレクトリ構成（予定）

```
docs/       規定、設計資料、調査メモ、大会記録
hardware/   回路図・基板 (KiCad)、機構 CAD、部品表 (BOM)
firmware/   機体のファームウェア
tools/      走行ログの解析、パラメータ調整などの PC 側ツール
```
