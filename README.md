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
│   ├── DateCalc.html           # Webフロントエンド
│   ├── DateCalc.py             # 計算ロジック
│   ├── DateCalc_server.py      # Flask Webサーバー（API）
│   ├── Dockerfile              # Webコンテナイメージ用
│   ├── gunicorn.conf.py        # Gunicorn設定
│   ├── requirements.txt        # 依存パッケージ（Flask・Gunicorn）
│   ├── test_DateCalc.py        # ユニットテスト（pytest）
│   └── wsgi.py                 # Gunicornエントリポイント
├── nginx/
│   ├── Dockerfile              # Nginxコンテナイメージ用
│   └── nginx.conf              # リバースプロキシ設定
├── .gitignore                  # Git管理除外設定
├── LICENSE                     # MITライセンス
├── README.md                   # プロジェクト説明
├── container-architecture.svg  # コンテナ構成図
├── docker-compose.yml          # コンテナ構成定義（ローカル開発用）
└── task-definition.json        # AWS ECSタスク定義
```

---

## コンテナ構成

<img src="container-architecture.svg" alt="コンテナ構成図" width="100%">

---

## GitHub Actions（CI/CD）

mainへのpushとpull requestをトリガーに実行

- **push**：test → build → push → deployすべて実行
- **pull request**：test → buildのみ実行（pushとdeployはスキップ）

同時実行制御（concurrency）はジョブ単位で設定
 
- **test / build / push**：古いコミットの実行をキャンセルし、最新コミットを優先
- **deploy**：実行中はキャンセルせず、新しい実行は前のデプロイ完了まで待機

---

| No. | ジョブ | ステップ | 処理内容 |
|-----|--------|-----------|---------|
| 1  | test   | Checkout repository                  | リポジトリをチェックアウト |
| 2  | test   | Set up Python                        | Python3.14環境をセットアップ |
| 3  | test   | Install dependencies                 | pipで依存パッケージをインストール |
| 4  | test   | Run tests                            | pytestでユニットテストを実行 |
| 5  | build  | Checkout repository                  | リポジトリをチェックアウト |
| 6  | build  | Extract metadata for web image       | Webイメージのタグ・ラベルを生成 |
| 7  | build  | Extract metadata for nginx image     | Nginxイメージのタグ・ラベルを生成 |
| 8  | build  | Set up Docker Buildx                 | BuildKitを有効化 |
| 9  | build  | Build web image                      | Webイメージをビルド（tar出力） |
| 10 | build  | Build nginx image                    | Nginxイメージをビルド（tar出力） |
| 11 | build  | Upload web image artifact            | WebイメージをArtifactに保存（PR時スキップ） |
| 12 | build  | Upload nginx image artifact          | NginxイメージをArtifactに保存（PR時スキップ） |
| 13 | push   | Login to GHCR                        | GITHUB_TOKENでGHCRにログイン |
| 14 | push   | Download web image artifact          | WebイメージをArtifactから取得 |
| 15 | push   | Push web image                       | WebイメージをGHCRにプッシュしdigest取得 |
| 16 | push   | Download nginx image artifact        | NginxイメージをArtifactから取得 |
| 17 | push   | Push nginx image                     | NginxイメージをGHCRにプッシュしdigest取得 |
| 18 | push   | Output image digest                  | タグ・digestをサマリーに出力 |
| 19 | deploy | Checkout repository                  | リポジトリをチェックアウト |
| 20 | deploy | Configure AWS credentials            | OIDCでAWS認証情報を取得 |
| 21 | deploy | Inject executionRoleArn              | 実行ロールARNのプレースホルダーを置換 |
| 22 | deploy | Render ECS task definition for web   | タスク定義のWebイメージをdigestで更新 |
| 23 | deploy | Render ECS task definition for nginx | タスク定義のNginxイメージをdigestで更新 |
| 24 | deploy | Deploy to ECS                        | ECSサービスにデプロイし安定化まで待機 |
　  
　  
　  

---

Copyright (c) 2026 Horikawa Takato  
Released under the MIT License
