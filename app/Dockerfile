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
