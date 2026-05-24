# 日数計算機

現在の日付と入力した日付の差分を計算します。
Dockerを使用したWebアプリケーションです。

---

## 主な機能

- 現在の日付と入力した日付の差分を日数で表示（365日以上は年数も併記）
- 紀元前999年から西暦9999年まで対応
- 紀元前の年は負数で入力（例：-100年1月1日 = 紀元前100年1月1日）
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

### Docker

| OS | 必要なソフトウェア | 備考 |
|---|---|---|
| Windows 10 / 11 | Docker Desktop 4.0 以上 | WSL2 が有効であること |
| macOS 12 以上 | Docker Desktop 4.0 以上 | Apple Silicon (M1/M2/M3) でも動作可 |
| Linux | Docker Engine 20.10 以上 + Docker Compose V2 | Docker Desktop でも可 |

#### Windows の WSL2 有効化確認

PowerShell（管理者）で以下を実行し、`Default Version: 2` と表示されれば有効です。

```powershell
wsl --status
```

表示されない場合は以下で有効化します。

```powershell
wsl --install
```

### コンテナ内の主要コンポーネント

| コンポーネント | バージョン | 役割 |
|---|---|---|
| Python | 3.12 | アプリケーション実行環境 |
| Flask | 3.1.0 | Webフレームワーク |
| Gunicorn | 23.0.0 | WSGIサーバー |
| Nginx | 1.27 (alpine) | リバースプロキシ |

### ブラウザ

Chrome / Edge / Firefox の最新版を推奨します。
アクセスURL：`http://localhost`

### GitHubアカウント（GHCRを利用する場合）

- GitHubアカウントが必要です
- Personal Access Token (PAT) のスコープ
  - イメージを取得するだけの場合：`read:packages`
  - イメージをpushする場合：`read:packages` `write:packages`

---

## セットアップ

### 方法1：GitHub Container Registry (GHCR) からイメージを取得して起動する（推奨）

ビルド不要でGHCRに公開済みのイメージをそのまま使用できます。

#### 1. Docker Desktop を起動する

#### 2. GHCRにログイン する

GitHubの Personal Access Token (PAT) が必要です。
PATは GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic) から作成します。
必要なスコープ： `read:packages`

```powershell
# Windows (PowerShell)
$env:CR_PAT = "ghp_xxxxxxxxxxxxxxxxxxxx"
$env:CR_PAT | docker login ghcr.io -u GitHubユーザー名 --password-stdin
```

```bash
# Mac / Linux
export CR_PAT=ghp_xxxxxxxxxxxxxxxxxxxx
echo $CR_PAT | docker login ghcr.io -u GitHubユーザー名 --password-stdin
```

#### 3. リポジトリをクローンする

```
git clone https://github.com/horikawatakato/DateCalc.git
cd DateCalc
```

#### 4. コンテナを起動する

```
docker compose up -d
```

GHCRからイメージを自動取得して起動します。ビルドは不要です。

---

### 方法2：ローカルでビルドして起動する（開発向け）

#### 1. Docker Desktop を起動する

#### 2. リポジトリをクローンする

```
git clone https://github.com/horikawatakato/DateCalc.git
cd DateCalc
```

#### 3. イメージをビルドして起動する

```
docker build -f app/Dockerfile -t ghcr.io/horikawatakato/datecalc:latest app
docker compose up -d
```

以下のログが表示されれば起動成功です。

```
web-1    | [INFO] Booting worker with pid: ...
nginx-1  | Configuration complete; ready for start up
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

### ログ確認

```
docker compose logs
```

### 停止

```
docker compose down
```

コンテナを停止して削除します。イメージはそのまま残るため、次回起動時に再ビルドは不要です。

### 最新イメージへの更新

GHCRに新しいイメージがpushされた場合は以下で更新できます。

```
docker compose pull
docker compose up -d
```

---

## GitHub Container Registry (GHCR) へのpush手順

開発者向けの手順です。イメージを更新してGHCRに反映する場合に実施します。

### 1. PATの準備

GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic) から作成。
必要なスコープ： `write:packages` `read:packages`

### 2. GHCRにログイン

```powershell
# Windows (PowerShell)
$env:CR_PAT = "ghp_xxxxxxxxxxxxxxxxxxxx"
$env:CR_PAT | docker login ghcr.io -u horikawatakato --password-stdin
```

### 3. イメージをビルド

```
docker build -f app/Dockerfile -t ghcr.io/horikawatakato/datecalc:latest app
```

### 4. GHCRへpush

```
docker push ghcr.io/horikawatakato/datecalc:latest
```

公開済みイメージは以下で確認できます。
https://github.com/horikawatakato?tab=packages

