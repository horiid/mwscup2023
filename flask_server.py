from flask import Flask, render_template, request, send_file
import csv, json

app=Flask(__name__, template_folder='template')

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

@app.route('/detail')
def detail():
    file_name = request.args.get('file_name')

    data = read_csv(file_name)
    return render_template("detail.html", data=data) # templatesフォルダ内のindex.htmlを表示する

def read_csv(file_name):
    with open('./data/' + file_name, mode='r', encoding="utf-8") as f:
        data = list(csv.reader(f))
    return data

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
