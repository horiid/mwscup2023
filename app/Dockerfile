# pythonイメージを取得
FROM python:3.10-slim-buster

# コンテナの作業ディレクトリ
WORKDIR /wide-angel

# アプリ資材のコピー
COPY . .

RUN pip install --upgrade pip
RUN pip install --upgrade setuptools

# ライブラリをインストール
RUN pip install -r requirements.txt

# 環境変数の設定
ENV FLASK_APP ./main
ENV FLASK_ENV produciton

# コンテナの実行
CMD ["flask", "run", "--host=0.0.0.0"]
