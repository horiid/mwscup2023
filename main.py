def get_rss():
    import feedparser
    url = "https://scan.netsecurity.ne.jp/rss/index.rdf"
    feed = feedparser.parse(url)
    for entry in feed.entries:
        print("%s\n%s\n%s\n\n"%(entry.title, entry.updated,  entry.link))
        if "ドコモ" in entry.title:
            return entry

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
    article = get_rss()
    send_line_notification(msg=article.title, link=article.link)