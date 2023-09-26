services = ["amazon", "ドコモ", "楽天", "サイボウズ"]
keywords = ["情報流出", "自動音声", "注意"]


def get_rss():
    import feedparser
    url = "https://scan.netsecurity.ne.jp/rss/index.rdf"
    feed = feedparser.parse(url)
    links = []
    for entry in feed.entries:
        for service in services:
            for keyword in keywords:
                if service in entry.title and keyword in entry.title:
                    if entry.link not in links:
                        send_line_notification(
                            msg=entry.title, link=entry.link)
                        print("%s\n%s\n%s\n\n" %
                              (entry.title, entry.updated,  entry.link))
                        links.append(entry.link)


def send_line_notification(msg, link):
    import requests
    token = "APITOKEN"

    # LINEメッセージを送る
    url = "https://notify-api.line.me/api/notify"  # APIのエンドポイント
    headers = {"Authorization": "Bearer " + token}
    payload = {"message": msg + "\n" + link}
    requests.post(url, headers=headers, data=payload)


if __name__ == '__main__':
    # main()
    get_rss()
    # send_line_notification(msg=article.title, link=article.link)
