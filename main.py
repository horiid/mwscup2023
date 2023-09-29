#!/usr/bin/env python3

import os

import feedparser
import requests
# import sys
import csv
from flask import Flask, render_template, request, send_file
from flask_apscheduler import APScheduler #定期実行のために必要なモジュール（flask用）
from dotenv import load_dotenv
from datetime import datetime, timedelta

load_dotenv()  # 環境変数の読み込み

scheduler = APScheduler()#定期実行のために必要なモジュール
app = Flask(__name__)

services = ["amazon", "ドコモ", "楽天", "サイボウズ", "クレディセゾン", "NHK"]
# keywords = ["情報流出", "自動音声", "注意", "情報漏えい"]
URL = "https://scan.netsecurity.ne.jp/rss/index.rdf"
FILE_NAME = "search_words.csv"
DIFF_JST_FROM_UTC = 9


@scheduler.task('interval',id="get_rss", hours=6)
def get_rss():
    feed = feedparser.parse(URL)
    links = []
    keywords = read_csv(FILE_NAME)
    # 現在時刻取得
    now = datetime.utcnow() + timedelta(hours=DIFF_JST_FROM_UTC)
    for entry in feed.entries:
        news_date = datetime.fromisoformat(entry.updated[:-1])  # "Z"を除去してISO 8601形式の文字列をDatetimeに変換
        # 記事の時刻と現在時刻を比較
        if now - timedelta(hours=6) < news_date:
            for service in services:
                for keyword in keywords:
                    if service in entry.title and keyword in entry.title:
                        if entry.link not in links:
                            send_line_notification(msg=entry.title, link=entry.link)
                            print("%s\n%s\n%s\n\n" % (entry.title, entry.updated, entry.link))
                            links.append(entry.link)

def read_csv(file_name):
    words_list = []

    with open(file_name, encoding="utf-8", newline="") as f:
        cr = csv.reader(f)
        for row in cr:
            words_list.append(row[0])
    
    return words_list

def send_line_notification(msg, link):
    token = os.environ.get("API_KEY", False)
    if token == False:
        print("Error: Cannot read LINE Notify API Key")
        return

    # LINEメッセージを送る
    url = "https://notify-api.line.me/api/notify"  # APIのエンドポイント
    headers = {"Authorization": "Bearer " + token}
    payload = {"message": msg + "\n" + link}
    requests.post(url, headers=headers, data=payload)


scheduler.init_app(app)
scheduler.start()


if __name__ == "__main__":
    # get_rss()
    # send_line_notification(msg=article.title, link=article.link)

    app.debug = True
    app.run(host= "localhost")