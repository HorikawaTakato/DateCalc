# 日数計算機

現在の日付と入力した日付の差分を計算するWebアプリケーションです。  
以下のURLからアクセスできます。  
http://ec2-3-114-247-73.ap-northeast-1.compute.amazonaws.com

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
│       └── build-push.yml    # GitHub Actions：テスト・ビルド・ECS 自動デプロイ
├── docker-compose.yml        # コンテナ構成定義（ローカル開発用）
├── task-definition.json      # AWS ECS タスク定義
├── .gitignore
├── nginx/
│   ├── nginx.conf            # リバースプロキシ設定
│   └── Dockerfile            # カスタム Nginx イメージ用
└── app/
    ├── Dockerfile
    ├── requirements.txt      # 依存パッケージ（Flask・Gunicorn）
    ├── gunicorn.conf.py      # Gunicorn 設定
    ├── wsgi.py               # Gunicorn エントリポイント
    ├── DateCalc.py           # 計算ロジック
    ├── DateCalc_server.py    # Flask Web サーバー（API）
    ├── DateCalc.html         # Web フロントエンド
    └── test_DateCalc.py      # ユニットテスト（pytest）
```

---

## コンテナ構成

<img src="container-architecture.svg" alt="コンテナ構成図" width="100%">

---

## CI/CD（GitHub Actions + GHCR + AWS ECS）

`main` ブランチへの Push をトリガーに、テスト・ビルド・デプロイが自動実行されます。

### ワークフローの流れ

```
コードを main ブランチへ Push
  ↓
GitHub Actions 起動（.github/workflows/build-push.yml）
  ↓
【test ジョブ】
Python 3.14 セットアップ・依存パッケージインストール
  ↓
pytest によるユニットテスト実行（42テスト）
  ↓（テスト失敗時はここで停止）
【build-and-push ジョブ】
GHCR へ自動ログイン
  ↓
app イメージをビルド＆Push（ghcr.io/horikawatakato/datecalc）
nginx イメージをビルド＆Push（ghcr.io/horikawatakato/datecalc-nginx）
タグを自動生成（latest / sha-xxxxxxx / ブランチ名）
  ↓
【deploy ジョブ】
AWS OIDC 認証（アクセスキー不要・安全）
  ↓
実行中の古い ECS タスクを停止（ポート解放）
  ↓
ECS タスク定義を新しいイメージで更新（web・nginx 各コンテナ）
  ↓
ECS サービスにデプロイ・安定確認（約3〜6分）
```

---

## AWS ECS 構成

### リソース一覧

| リソース | 名前 | 備考 |
|---|---|---|
| ECS クラスター | `datecalc-cluster` | EC2 起動タイプ |
| ECS サービス | `datecalc-service` | タスク数：1 |
| ECS タスク定義 | `datecalc-task` | 2コンテナ構成 |
| EC2 インスタンス | `t3.micro` | 無料枠対象 |
| Elastic IP | `3.114.247.73` | EC2 再起動後も IP 固定 |
| IAM ロール（デプロイ用） | `GitHubActionsECSDeployRole` | OIDC 認証 |
| IAM ロール（タスク実行用） | `ecsTaskExecutionRole` | イメージ Pull 用 |
| CloudWatch Logs | `/ecs/datecalc` | コンテナログ |
| リージョン | `ap-northeast-1`（東京） | |

### タスク定義

| コンテナ名 | イメージ | ポート | メモリ |
|---|---|---|---|
| web | `ghcr.io/horikawatakato/datecalc` | 8000（内部のみ） | 200MB |
| nginx | `ghcr.io/horikawatakato/datecalc-nginx` | 80（外部公開） | 100MB |

### ログの確認

AWS CloudWatch Logs でコンテナのログを確認できます。

| ロググループ | プレフィックス | 対象 |
|---|---|---|
| `/ecs/datecalc` | `ecs` | web コンテナ（Gunicorn） |
| `/ecs/datecalc` | `ecs-nginx` | nginx コンテナ |
