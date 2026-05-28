# 日数計算機

日数計算を行うWebアプリケーションです。  
AWS ECS on EC2でコンテナ運用し、GitHub ActionsによるCI/CDを構築しています。

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
│       └── cicd.yml            # GitHub Actions
├── app/
│   ├── DateCalc.html           # Web フロントエンド
│   ├── DateCalc.py             # 計算ロジック
│   ├── DateCalc_server.py      # Flask Web サーバー（API）
│   ├── Dockerfile
│   ├── gunicorn.conf.py        # Gunicorn 設定
│   ├── requirements.txt        # 依存パッケージ（Flask・Gunicorn）
│   ├── test_DateCalc.py        # ユニットテスト（pytest）
│   └── wsgi.py                 # Gunicorn エントリポイント
├── nginx/
│   ├── Dockerfile              # カスタム Nginx イメージ用
│   └── nginx.conf              # リバースプロキシ設定
├── .gitignore                  # Git 管理除外設定
├── LICENSE                     # MITライセンス
├── README.md                   # プロジェクト説明
├── container-architecture.svg  # コンテナ構成図
├── docker-compose.yml          # コンテナ構成定義（ローカル開発用）
└── task-definition.json        # AWS ECS タスク定義
```

---

## コンテナ構成

<img src="container-architecture.svg" alt="コンテナ構成図" width="100%">

---

## GitHub Actions（CI/CD）

mainへのpushをトリガーに、以下の処理が順番に自動で実行されます。

---

| No. | ジョブ | ステップ | 処理内容 |
|-----|--------|-----------|---------|
| 1  | test           | Checkout repository                  | リポジトリをチェックアウト |
| 2  | test           | Set up Python                        | Python3.14環境をセットアップ |
| 3  | test           | Install dependencies                 | pipで依存パッケージをインストール |
| 4  | test           | Run tests                            | pytestでユニットテストを実行 |
| 5  | build-and-push | Checkout repository                  | リポジトリをチェックアウト |
| 6  | build-and-push | Login to GHCR                        | GITHUB_TOKENでGHCRに認証ログイン |
| 7  | build-and-push | Extract metadata (tags & labels)     | Webアプリイメージのタグ・ラベルを生成 |
| 8  | build-and-push | Set up Docker Buildx                 | BuildKitを有効化 |
| 9  | build-and-push | Build and push image                 | WebアプリイメージをビルドしGHCRにプッシュ |
| 10 | build-and-push | Extract metadata for nginx image     | Nginxイメージのタグ・ラベルを生成 |
| 11 | build-and-push | Build and push nginx image           | NginxイメージをビルドしGHCRにプッシュ |
| 12 | build-and-push | Output image digest                  | プッシュしたイメージ情報をサマリーに出力 |
| 13 | deploy         | Checkout repository                  | リポジトリをチェックアウト |
| 14 | deploy         | Configure AWS credentials            | OIDCでAWSに認証 |
| 15 | deploy         | Stop running tasks                   | 稼働中の旧ECSタスクを停止しポートを解放 |
| 16 | deploy         | Get short SHA                        | コミットSHAの先頭7文字を生成 |
| 17 | deploy         | Render ECS task definition for web   | タスク定義のwebコンテナイメージを更新 |
| 18 | deploy         | Render ECS task definition for nginx | タスク定義のnginxコンテナイメージを更新 |
| 19 | deploy         | Deploy to ECS                        | ECSサービスにデプロイし安定化まで待機 |

---

Copyright (c) 2026 Horikawa Takato  
Released under the MIT License
