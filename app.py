from flask import Flask, render_template, request
from datetime import datetime, timedelta
import os

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':



        userName = request.form.get('userName')
        dates = request.form.getlist('date')
        start_times = request.form.getlist('start_time')
        end_times = request.form.getlist('end_time')
        results = []

        # ユーザーごとにファイルを書き込む
        base_dir = os.path.abspath(os.path.dirname(__file__))
        file_path1 = os.path.join(base_dir, 'usersDate', f'{userName}.txt')
        file_path2 = os.path.join(base_dir, 'data.txt')
        with open(file_path1, 'a', encoding='UTF-8') as f:
            # data.txtにも書き込む 算出用
            with open(file_path2, 'a', encoding='utf-8') as b:
                for date, start_time, end_time in zip(dates, start_times, end_times):
                    results.append(f'日付: {date}, 開始時間: {start_time}, 終了時間: {end_time}')
                    f.write(f'{date} {start_time} {end_time}\n')
                    b.write(f'{date} {start_time} {end_time}\n')

        return '<br>'.join(results)
    return render_template('index.html')

@app.route('/findDate', methods=['GET', 'POST'])
def findDate():
    # 投稿者を特定
    base_dir = os.path.abspath(os.path.dirname(__file__))
    folderPath = os.path.join(base_dir, 'usersDate')
    
    userData = []
    for usersFile in os.listdir(folderPath):
        if usersFile.endswith('.txt'):
            file_path = os.path.join(folderPath, usersFile)
            file_size = os.path.getsize(file_path)
            if file_size > 0:
                userData.append(usersFile[:-4])

    if request.method == 'POST':
        filePath = os.path.join(base_dir, 'data.txt')
        # data.txtを全て読み込む
        ng_data = []
        with open(filePath, 'r', encoding='utf-8') as base:
            content = base.read()
            ng_data.append(content)

        # NG時間の処理
        ng_times = []
        for line in ng_data:
            for entry in line.splitlines():
                parts = entry.split()
                if len(parts) >= 3:  # 3つ以上の要素がある場合のみ処理
                    date, start_time, end_time = parts[0], parts[1], parts[2]
                    ng_times.append((datetime.strptime(f"{date} {start_time}", "%Y-%m-%d %H:%M"),
                                     datetime.strptime(f"{date} {end_time}", "%Y-%m-%d %H:%M")))

        # 設定された期日をdatetimeに変換
        start = request.form.get('start')
        end = request.form.get('end')
        dt1 = datetime.strptime(start, "%Y-%m-%d")
        dt2 = datetime.strptime(end, "%Y-%m-%d")

        # 時間を指定して新しいdatetimeオブジェクトを作成
        start_date = dt1.replace(hour=9, minute=0)
        end_date = dt2.replace(hour=18, minute=0)
        # 利用可能な時間帯を保存するリスト
        available_ranges = []

        # 現在の時間を設定
        current_time = start_date
        while current_time < end_date:
            if (current_time.hour >= 9 and current_time.hour < 12) or (current_time.hour > 12 and current_time.hour < 18):
                if not any(start <= current_time < end for start, end in ng_times):
                    if not available_ranges or available_ranges[-1][1] < current_time - timedelta(minutes=1):
                        available_ranges.append([current_time, current_time])
                    else:
                        available_ranges[-1][1] = current_time
            current_time += timedelta(minutes=1)

        # 時間帯をフォーマットして色を設定
        formatted_ranges = []
        for start, end in available_ranges:
            start_time = start
            end_time = end
            duration = (end_time - start_time).seconds / 3600  # 時間に変換
            color = 'red' if duration >= 1 else 'black'  # 色を決定
            formatted_ranges.append((start_time.strftime('%Y-%m/%d %H:%M'), end_time.strftime('%H:%M'), color))

        return render_template('findDate.html', userData=userData, available_ranges=formatted_ranges)

    return render_template('findDate.html', userData=userData)

@app.route('/deleteDate', methods=['POST'])
def delete_all_user_data():
    base_dir = os.path.abspath(os.path.dirname(__file__))
    folderPath = os.path.join(base_dir, 'usersDate')

    # usersDateフォルダ内のすべてのファイルを削除
    for file_name in os.listdir(folderPath):
        file_path = os.path.join(folderPath, file_name)
        if os.path.isfile(file_path):
            os.remove(file_path)

    # data.txtも削除
    data_file_path = os.path.join(base_dir, 'data.txt')
    if os.path.exists(data_file_path):
        os.remove(data_file_path)

    return redirect('/findDate')

if __name__ == '__main__':
    app.run(debug=True)
