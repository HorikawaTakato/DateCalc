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
datecalc/
├── .github/
│   └── workflows/
│       └── build-push.yml   # GitHub Actions：自動ビルド＆GHCRプッシュ
├── docker-compose.yml        # コンテナ構成定義
├── .gitignore
├── nginx/
│   └── nginx.conf            # リバースプロキシ設定
└── app/
    ├── Dockerfile
    ├── requirements.txt      # 依存パッケージ
    ├── gunicorn.conf.py      # Gunicorn設定
    ├── wsgi.py               # Gunicornエントリポイント
    ├── DateCalc.py           # 計算ロジック
    ├── DateCalc_server.py    # Flask Webサーバー（API）
    ├── DateCalc.html         # Webフロントエンド
    └── test_DateCalc.py      # ユニットテスト（pytest）
```

---

## CI/CD（GitHub Actions + GHCR）

`main` ブランチへのプッシュをトリガーに、イメージのビルドとGHCRへのプッシュが自動実行されます。

### ワークフローの流れ

```
コードを main ブランチへ Push
  ↓
GitHub Actions 起動（.github/workflows/build-push.yml）
  ↓
Python 3.14 セットアップ・依存パッケージインストール
  ↓
pytest によるユニットテスト実行
  ↓（テスト失敗時はここで停止）
GITHUB_TOKEN 自動発行（追加シークレット不要）
  ↓
GHCR へ自動ログイン
  ↓
イメージをビルド（GHCRのキャッシュを活用して高速化）
  ↓
タグを自動生成（latest / sha-xxxxxxx / ブランチ名）
  ↓
ghcr.io/horikawatakato/datecalc へ Push
```

### 自動生成されるタグ

| Gitイベント | 生成されるタグ例 |
|---|---|
| `main` へのプッシュ | `latest`, `main`, `sha-abc1234` |
| `v1.2.3` タグのプッシュ | `1.2.3`, `1.2`, `1`, `latest` |
| プルリクエスト | `pr-42`（GHCRへのプッシュはスキップ） |

### イメージに埋め込まれるメタデータ

Dockerfileの `ARG` を通じて、以下の情報がOCIラベルとしてイメージに記録されます。
GHCR の「Package」ページで確認できます。

| ラベル | 内容 |
|---|---|
| `org.opencontainers.image.created` | ビルド日時（ISO8601形式） |
| `org.opencontainers.image.revision` | ビルド元のコミットSHA |
| `org.opencontainers.image.source` | リポジトリURL |
| `org.opencontainers.image.version` | イメージバージョン |

### ワークフロー実行結果の確認

GitHub リポジトリの「Actions」タブでビルドの成否と以下の情報を確認できます。

```
✅ Image pushed to GHCR
┌──────────┬──────────────────────────────────────────┐
│ Registry │ ghcr.io                                  │
│ Image    │ horikawatakato/datecalc                  │
│ Digest   │ sha256:abc123...                         │
│ Tags     │ latest, main, sha-abc1234                │
└──────────┴──────────────────────────────────────────┘
```

---

## 動作環境

### Docker

| OS | 必要なソフトウェア | 備考 |
|---|---|---|
| Windows 10 / 11 | Docker Desktop 4.0 以上 | WSL2 が有効であること |
| macOS 12 以上 | Docker Desktop 4.0 以上 | Apple Silicon (M1/M2/M3) でも動作可 |
| Linux | Docker Engine 20.10 以上 + Docker Compose V2 | Docker Desktop でも可 |

Docker Desktop のダウンロードはこちら：https://www.docker.com/products/docker-desktop/

インストール後、以下のコマンドでバージョンを確認できます。

```
docker --version
docker compose version
```

#### Windows：WSL2 の有効化確認

Docker Desktop for Windows は WSL2 が必須です。
PowerShell（管理者）で以下を実行します。

```powershell
wsl --status
```

`Default Version: 2` と表示されれば有効です。
表示されない場合は以下で WSL2 をインストールします。

```powershell
wsl --install
```

インストール後、PCを再起動してから Docker Desktop を起動してください。

#### Linux：Docker Engine と Docker Compose V2 のインストール確認

```bash
# Docker Engine のバージョン確認
docker --version

# Docker Compose V2 のバージョン確認（compose サブコマンドで動作するか確認）
docker compose version
```

`docker-compose`（ハイフンあり）は旧バージョン（V1）です。
本アプリは `docker compose`（スペース区切り・V2）を使用します。

---

### コンテナ内の主要コンポーネント

| コンポーネント | バージョン | 役割 |
|---|---|---|
| Python | 3.14 (slim) | アプリケーション実行環境 |
| Flask | 3.1.0 | Webフレームワーク |
| Gunicorn | 23.0.0 | WSGIサーバー（本番向け） |
| Nginx | 1.27 (alpine) | リバースプロキシ |

#### コンテナ構成

```
ブラウザ
  ↓ http://localhost:80
Nginx（リバースプロキシ）
  ↓ http://web:8000
Gunicorn + Flask（アプリケーションサーバー）
```

Nginx がポート80でリクエストを受け取り、コンテナ内部のGunicorn（ポート8000）に転送します。
Gunicornのポートは外部に公開されておらず、Nginxからのみアクセス可能です。

---

### ブラウザ

| ブラウザ | 推奨バージョン |
|---|---|
| Google Chrome | 最新版 |
| Microsoft Edge | 最新版 |
| Mozilla Firefox | 最新版 |
| Safari | 最新版（macOS） |

アクセスURL：`http://localhost`

> ℹ️ HTTPS には対応していません。`https://localhost` ではアクセスできません。

---

### Git（リポジトリをクローンする場合）

ソースコードをクローンするために Git が必要です。

- Windows：https://git-scm.com/download/win からインストール
- macOS：`xcode-select --install` でインストール（または Homebrew: `brew install git`）
- Linux：`sudo apt install git`（Debian/Ubuntu系）

インストール確認：

```
git --version
```

---

## セットアップ

### 方法1：GitHub Container Registry (GHCR) からイメージを取得して起動する（推奨）

GHCRのイメージはPublicで公開されています。
イメージの取得（pull）に認証は不要です。ビルドは不要です。

#### 1. Docker Desktop を起動する

スタートメニュー（Windows）または Launchpad（Mac）から Docker Desktop を起動します。
タスクバー右下（Windows）またはメニューバー（Mac）のクジラアイコンが静止したら起動完了です。

起動確認コマンド：

```
docker info
```

エラーなく情報が表示されれば起動しています。

#### 2. リポジトリをクローンする

```
git clone https://github.com/horikawatakato/datecalc.git
```

クローンしたフォルダに移動します。

```
cd datecalc
```

#### 3. コンテナを起動する

```
docker compose up -d
```

初回はイメージのダウンロードが行われるため、数分かかる場合があります。

起動確認コマンド：

```
docker compose ps
```

`web` と `nginx` の両方の STATUS が `running` になれば起動完了です。
ブラウザで `http://localhost` を開いてアクセスします。

---

### 方法2：ローカルでビルドして起動する（開発向け）

アプリのソースコードを変更して動作確認したい場合に使用します。

#### 1. Docker Desktop を起動する

方法1の手順1と同様です。

#### 2. リポジトリをクローンする

```
git clone https://github.com/horikawatakato/datecalc.git
cd datecalc
```

#### 3. イメージをビルドする

```
docker build -f app/Dockerfile -t ghcr.io/horikawatakato/datecalc:latest app
```

- `-f app/Dockerfile`：Dockerfileのパスを指定
- 末尾の `app`：ビルドコンテキスト（app/フォルダ内のファイルを参照）

ビルドには数分かかる場合があります。`FINISHED` と表示されれば完了です。

#### 4. コンテナを起動する

```
docker compose up -d
```

起動確認コマンド：

```
docker compose ps
```

`web` と `nginx` の両方の STATUS が `running` になれば起動完了です。

以下のログが表示されれば正常に動作しています。

```
web-1    | [INFO] Booting worker with pid: ...
nginx-1  | Configuration complete; ready for start up
```

ログの確認コマンド：

```
docker compose logs
```

ブラウザで `http://localhost` を開いてアクセスします。

---

## 使い方

### 起動

```
docker compose up -d
```

`-d` オプションでバックグラウンド起動になります。
起動後、Webブラウザで `http://localhost` を開きます。

フォアグラウンドで起動してログをリアルタイムに確認したい場合は `-d` を省略します。

```
docker compose up
```

### 状態確認

```
docker compose ps
```

各コンテナの状態が表示されます。`STATUS` が `running` であれば正常に動作しています。

```
NAME              IMAGE                                    STATUS
datecalc-nginx-1  nginx:1.27-alpine                        running
datecalc-web-1    ghcr.io/horikawatakato/datecalc:latest   running
```

healthcheck が完了するまで `web` コンテナの STATUS は `starting` と表示されます。
`running` になるまで少し待ってからブラウザでアクセスしてください。

### ログ確認

全コンテナのログをまとめて確認します。

```
docker compose logs
```

特定のコンテナのログのみ確認する場合はサービス名を指定します。

```
# Flaskアプリのログ
docker compose logs web

# Nginxのログ
docker compose logs nginx
```

リアルタイムでログを流し続ける場合は `-f` を付けます。

```
docker compose logs -f
```

### 再起動

コンテナを再起動する場合は以下を実行します。

```
# 全コンテナを再起動
docker compose restart

# 特定のコンテナのみ再起動
docker compose restart web
```

### 停止

```
docker compose down
```

コンテナを停止して削除します。イメージはそのまま残るため、次回起動時に再ビルドは不要です。

イメージごと削除したい場合は `--rmi` オプションを付けます。

```
docker compose down --rmi all
```

### 最新イメージへの更新

`main` ブランチへのプッシュ後、GitHub Actions が自動的にビルド＆GHCRへのプッシュを行います。
新しいイメージへの更新は以下の手順で行います。

#### GHCR から最新イメージを取得して再起動する

```
docker compose pull
docker compose up -d
```

#### 特定のコミットSHAのイメージで起動する

GitHub Actions が自動生成した `sha-xxxxxxx` タグを指定して起動することで、
特定のコミット時点のイメージを使用できます。

```
# 例：コミット SHA が abc1234 の場合
IMAGE_TAG=sha-abc1234 docker compose up -d
```

または `.env` ファイルに記載して起動します。

```
# .env ファイル
IMAGE_TAG=sha-abc1234
```

```
docker compose up -d
```

> ℹ️ `IMAGE_TAG` を指定しない場合は `latest` タグのイメージが使用されます。

#### 更新前後のイメージを確認する

```
docker images | grep datecalc
```

#### イメージのビルド情報を確認する

GHCRにプッシュされたイメージには、ビルド日時とコミットSHAが記録されています。
以下のコマンドで確認できます。

```
docker inspect ghcr.io/horikawatakato/datecalc:latest \
  --format '{{index .Config.Labels "org.opencontainers.image.created"}} / {{index .Config.Labels "org.opencontainers.image.revision"}}'
```

出力例：

```
2025-05-24T10:00:00Z / abc1234def5678...
```
