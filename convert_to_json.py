import pandas as pd
import json
import os

# CSVファイルの読み込み
file_path = 'kansensyo/kansensyo_201501_202504.csv'
try:
    # まずShift-JISで試す
    df = pd.read_csv(file_path, encoding='shift_jis')
except UnicodeDecodeError:
    # Shift-JISで失敗した場合はUTF-8で試す
    print("Shift-JISでの読み込みに失敗しました。UTF-8で再試行します。")
    df = pd.read_csv(file_path, encoding='utf-8')

# 年と週をdatetimeに変換する関数
def year_week_to_date(row):
    try:
        week_str = str(row['週']).zfill(2)
        date_str = f"{row['年']}-{week_str}-0"
        return pd.to_datetime(date_str, format='%Y-%W-%w').strftime('%Y-%m-%d')
    except ValueError:
        return None

# 日付列を作成
df['date'] = df.apply(year_week_to_date, axis=1)
df = df.dropna(subset=['date'])

# 感染症名のリストを取得 (年、週、Dateカラムを除外)
infection_columns = [col for col in df.columns if col not in ['年', '週', 'date']]

# データを整形
data = {
    'dates': df['date'].tolist(),
    'infections': {}
}

# NumPy型をPythonの標準的な型に変換する関数
def convert_to_serializable(obj):
    if hasattr(obj, 'tolist'):
        return obj.tolist()
    elif hasattr(obj, 'item'):
        return obj.item()
    else:
        return obj

# 各感染症のデータを追加
for infection in infection_columns:
    data['infections'][infection] = [convert_to_serializable(x) for x in df[infection].tolist()]

# 年別集計データを作成
yearly_data = {}
for year in df['年'].unique():
    yearly_df = df[df['年'] == year]
    yearly_data[str(year)] = {}
    for infection in infection_columns:
        yearly_data[str(year)][infection] = convert_to_serializable(yearly_df[infection].sum())

# 最終的なJSONデータ
json_data = {
    'timeSeriesData': data,
    'yearlyData': yearly_data,
    'infectionNames': infection_columns
}

# JSONファイルに保存
os.makedirs('docs', exist_ok=True)
with open('docs/data.json', 'w', encoding='utf-8') as f:
    json.dump(json_data, f, ensure_ascii=False, indent=2)

print("データをJSONに変換し、docs/data.jsonに保存しました。")
