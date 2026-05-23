# ────────────────────────────────────────────
# ステージ1: 依存パッケージのインストール
# ────────────────────────────────────────────
FROM python:3.12-slim AS builder

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt


# ────────────────────────────────────────────
# ステージ2: 実行イメージ
# ────────────────────────────────────────────
FROM python:3.12-slim

# GHCR連携用ビルド引数（docker build --build-arg で上書き可能）
ARG IMAGE_VERSION=latest
ARG GITHUB_REPOSITORY=HorikawaTakato/DateCalc
ARG GITHUB_SERVER_URL=https://github.com

# OCI標準ラベル（GHCRがリポジトリと自動紐づけするために必要）
LABEL org.opencontainers.image.title="DateCalc" \
      org.opencontainers.image.description="Date calculation web app (Flask + Gunicorn)" \
      org.opencontainers.image.version="${IMAGE_VERSION}" \
      org.opencontainers.image.source="${GITHUB_SERVER_URL}/${GITHUB_REPOSITORY}" \
      org.opencontainers.image.licenses="MIT"

# セキュリティ: 非 root ユーザーで実行
RUN useradd --create-home appuser
WORKDIR /app

# インストール済みパッケージをコピー
COPY --from=builder /install /usr/local

# アプリファイルをコピー
#   DateCalc.py          … 計算ロジック
#   DateCalc_server.py   … Flask アプリ本体（変更なし）
#   DateCalc.html        … フロントエンド（/ で配信）
#   wsgi.py              … Gunicorn エントリポイント
#   gunicorn.conf.py     … Gunicorn 設定
COPY --chown=appuser:appuser . .

USER appuser

EXPOSE 8000

# Gunicorn 経由で起動（DateCalc_server.py の app.run() は呼ばれない）
CMD ["gunicorn", "--config", "gunicorn.conf.py", "wsgi:app"]
