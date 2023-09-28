import os

import feedparser
import requests
from dotenv import load_dotenv

load_dotenv()  # 環境変数の読み込み

services = ["amazon", "ドコモ", "楽天", "サイボウズ", "クレディセゾン"]
keywords = ["情報流出", "自動音声", "注意", "情報漏えい"]


def get_rss():
    url = "https://scan.netsecurity.ne.jp/rss/index.rdf"
    feed = feedparser.parse(url)
    links = []
    for entry in feed.entries:
        for service in services:
            for keyword in keywords:
                if service in entry.title and keyword in entry.title:
                    if entry.link not in links:
                        send_line_notification(msg=entry.title, link=entry.link)
                        print("%s\n%s\n%s\n\n" % (entry.title, entry.updated, entry.link))
                        links.append(entry.link)


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


if __name__ == "__main__":
    # main()
    get_rss()
    # send_line_notification(msg=article.title, link=article.link)
