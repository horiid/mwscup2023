#!/usr/bin/env python3

import csv
import json
from datetime import datetime, timedelta

import feedparser
from dotenv import load_dotenv
from flask import Flask, redirect, render_template, request, url_for
from flask_apscheduler import APScheduler  # 定期実行のために必要なモジュール（flask用）

from utils import read_csv, send_line_notification

load_dotenv()  # 環境変数の読み込み

scheduler = APScheduler()#定期実行のために必要なモジュール
app = Flask(__name__, template_folder='template/')

services = []
startup = True
URL = "https://scan.netsecurity.ne.jp/rss/index.rdf"
FILE_NAME = "search_words.csv"
DIFF_JST_FROM_UTC = 9
JSON_FILENAME = "services.json"
REGISTER_CSV_FILENAME = "register.csv"


@scheduler.task('interval',id="get_rss", hours=6)
def get_rss():
    """RSSフィードから記事を取得し、条件にマッチしたものをLINEで通知する

    Params:
        None

    Returns:
        None
    """
    feed = feedparser.parse(URL)
    links = []
    keywords = read_csv(FILE_NAME)
    with open(JSON_FILENAME, encoding="utf-8") as json_file:
        services_json_all = json.load(json_file)
    # 現在時刻取得
    now = datetime.utcnow() + timedelta(hours=DIFF_JST_FROM_UTC)
    
    for entry in feed.entries:
        news_date = datetime.fromisoformat(entry.updated[:-1])  # "Z"を除去してISO 8601形式の文字列をDatetimeに変換
        # 記事の時刻と現在時刻を比較
        if now - timedelta(hours=6) < news_date:
            for default_service in services:
                for service in services_json_all["services"][default_service]["service_names"]:
                    for keyword in keywords:
                        if service in entry.title and keyword in entry.title:
                            if entry.link not in links:
                                send_line_notification(msg=entry.title, link=entry.link)
                                print("%s\n%s\n%s\n\n" % (entry.title, entry.updated, entry.link))
                                links.append(entry.link)


@app.route('/')
@app.route('/top')
def top():
    """トップページを表示する
        top.htmlにservices及びservices_jsonを受け渡す

    Returns:
        render_template
    """
    global startup
    global services
    if startup == True:
        startup = False
        services = read_csv(REGISTER_CSV_FILENAME)

    with open(JSON_FILENAME, encoding="utf-8") as json_file:
        services_json_all = json.load(json_file)

    services_json = []
    for key in services_json_all["services"].keys():
        services_json.append(key)

    return render_template('top.html', services=services, services_json=services_json)


@app.route("/register", methods=["POST"])
def register_services():  
    """通知するサービスを登録するフォーム
    register.csvの更新・グローバル変数を変更後トップ画面にリダイレクトする
    
    Params:
        None
    
    Returns:
        redirect(url_for("top"))
    """  
    f = open(REGISTER_CSV_FILENAME, "w")
    writer = csv.writer(f)
    global services
    services = list()
    for service_name, status in request.form.items():
        if status == 'register':
            writer.writerow([service_name])
            services.append(service_name)
    f.close()
    return redirect(url_for('top'))


if __name__ == "__main__":
    scheduler.init_app(app)
    scheduler.start()
    app.debug = True # 最終的なmainブランチではdebugはFalseにする
    app.run(host= "localhost")
