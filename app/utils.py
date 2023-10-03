import os, requests, csv

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
