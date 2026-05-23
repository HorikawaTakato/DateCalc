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

- Docker Desktop 4.0 以上
  - Windows：WSL2 が有効であること
  - Mac / Linux：Docker Desktop または Docker Engine が起動していること
- ブラウザ：Chrome / Edge / Firefox など（最新版推奨）

---

## セットアップ

### 1. Docker Desktop を起動する

### 2. リポジトリをクローンする

```
git clone https://github.com/HorikawaTakato/DateCalc.git && cd DateCalc
```

### 3. イメージをビルドして起動する

```
docker compose up --build
```

以下のログが表示されれば起動成功です。

```
web-1    | [INFO] Booting worker with pid: ...
nginx-1  | Configuration complete; ready for start up
```

初回はイメージのダウンロードとビルドのため数分かかります。
2回目以降は `--build` を省略できます。

```
docker compose up
```

---

## 使い方

### 起動

```
docker compose up -d
```

`-d` オプションでバックグラウンド起動になります。  
起動後、Webブラウザで `http://localhost` を開きます。

### 状態確認

```
docker compose ps
```

`STATUS` が `running` であれば正常に動作しています。

### ログの確認

```
docker compose logs -f
```

`Ctrl+C` でログ表示を終了します（コンテナは停止しません）。

### 停止

```
docker compose down
```

コンテナを停止して削除します。イメージはそのまま残るため、  
次回起動時に再ビルドは不要です。
