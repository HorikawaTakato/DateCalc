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
├── docker-compose.yml       # コンテナ構成定義
├── .gitignore
├── nginx/
│   └── nginx.conf           # リバースプロキシ設定
└── app/
    ├── Dockerfile
    ├── requirements.txt     # 依存パッケージ
    ├── gunicorn.conf.py     # Gunicorn設定
    ├── wsgi.py              # Gunicornエントリポイント
    ├── DateCalc.py          # 計算ロジック
    ├── DateCalc_server.py   # Flask Webサーバー（API）
    └── DateCalc.html        # Webフロントエンド
```

---

## 動作環境

- Docker Desktop

---

## セットアップ

```
# リポジトリをクローン
git clone https://github.com/HorikawaTakato/DateCalc.git
cd DateCalc

# イメージをビルドして起動
docker compose up --build
```

---

## 使い方

```
# 起動
docker compose up -d
```

起動後、Webブラウザで `http://localhost` を開きます。

```
# 停止
docker compose down
```
