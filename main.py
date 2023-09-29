#!/usr/bin/env python3

import os

import feedparser
import requests
# import sys
import csv
import json
from flask import Flask, render_template, request, send_file
from flask_apscheduler import APScheduler #定期実行のために必要なモジュール（flask用）
from dotenv import load_dotenv
from datetime import datetime, timedelta

load_dotenv()  # 環境変数の読み込み

scheduler = APScheduler()#定期実行のために必要なモジュール
app = Flask(__name__, template_folder='template/')

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


@app.route('/')
@app.route('/top')
def top():
    category = ['社会​', '気象・災害​', '科学・文化​', '政治​', 'ビジネス​', 'スポーツ​', '暮らし​', '医療・健康​']
    csv_name = ['1.csv', '2.csv', '3.csv', '4.csv', '5.csv', '6.csv', '7.csv', '8.csv']
    cat_url = dict(zip(category, csv_name))
    return render_template('top.html', cat_url=cat_url)

@app.route("/download")
def download():
    csv_name = request.args.get('fname_ext').split(',')[0]
    extention = request.args.get('fname_ext').split(',')[1]
    csv_path = './data/' + csv_name
    if extention == 'csv':
        return send_file(csv_path, as_attachment=True, download_name=csv_name, mimetype='text/csv')
    elif extention == 'json':
        # CSVファイルの読み込み
        with open(file=csv_path, mode='r', encoding="utf-8") as f:
            d_reader = csv.DictReader(f)
            d_list = [row for row in d_reader]

        # JSONファイルへの書き込み
        json_name = csv_name.replace('csv', 'json')
        json_path = './data/' + json_name
        with open(file=json_path, mode='w', encoding="utf-8") as f:
            json.dump(d_list, f, ensure_ascii=False)
        return send_file(json_path, as_attachment=True, download_name=json_name, mimetype='application/json')

def flask_read_csv(file_name):
    with open('./data/' + file_name, mode='r', encoding="utf-8") as f:
        data = list(csv.reader(f))
    return data


@app.route('/detail')
def detail():
    file_name = request.args.get('file_name')

    data = flask_read_csv(file_name)
    return render_template("detail.html", data=data) # templatesフォルダ内のindex.htmlを表示する


if __name__ == "__main__":
    # get_rss()
    # send_line_notification(msg=article.title, link=article.link)

    app.debug = True
    app.run(host= "localhost")