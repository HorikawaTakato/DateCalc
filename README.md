# 日数計算機

現在の日付と入力した日付の差分を計算するツールです。  
Webブラウザで使用できます。

---

## 主な機能

- 現在の日付と入力した日付の差分を日数で表示（365日以上は年数も併記）
- 紀元前999年から西暦9999年まで対応
- 紀元前の年は負数で入力（例：-100年1月1日= 紀元前100年1月1日）
- 曜日の表示
- 計算履歴の表示（最大8件、重複は自動排除）

---

## ファイル構成

```
DateCalc/
├── DateCalc.html        # Webフロントエンド
├── DateCalc.py          # 計算ロジック
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
