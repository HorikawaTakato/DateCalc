# 日数計算機 DateCalc

入力した日付と今日の差分を計算するツールです。  
紀元前999年から西暦9999年まで対応しています。

Webブラウザで使用できます。

---

## 主な機能

- 指定日と今日の差分を日数で表示（365日以上は年数も併記）
- 紀元前の日付に対応（例：`-100 3 15` = 紀元前100年3月15日）
- 曜日の自動計算
- 計算履歴の管理（最大8件、重複は自動排除）

---

## ファイル構成

```
DateCalc/
├── DateCalc.html        # Webフロントエンド
├── DateCalc.py          # 計算ロジック + CLIインターフェース
├── DateCalc_server.py   # Flask Webサーバー（API）
├── DateCalc_test.py     # テスト
└── requirements.txt     # 依存パッケージ
```

---

## 動作環境

- Python 3.10 以上
- Flask

---

## セットアップ

```
# リポジトリをクローン
git clone https://github.com/HorikawaTakato/DateCalc.git
cd DateCalc

# 依存パッケージをインストール
pip install -r requirements.txt
```

---

## 使い方

```
# サーバーを起動
python DateCalc_server.py
```

起動後、Webブラウザで `http://localhost:5000` を開きます。  
`Ctrl+C` でサーバーを停止できます。
