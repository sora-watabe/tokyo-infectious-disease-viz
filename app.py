import streamlit as st
import pandas as pd
import plotly.express as px # Plotlyをインポート
# from sklearn.linear_model import LinearRegression # Removed import
# import numpy as np # Removed import

# 年と週をdatetimeに変換する関数
def year_week_to_date(row):
    # 週の始まりを日曜(0)と仮定して日付を計算
    # %W は週番号 (月曜日始まり)、%U は週番号 (日曜日始まり)
    # %w は曜日 (0=日曜日)
    # ISO週番号 (%G-%V-%u) を使う方がより正確かもしれないが、データの形式に合わせる
    try:
        # 週番号が1桁の場合、ゼロパディングする
        week_str = str(row['週']).zfill(2)
        # 年-週番号-曜日(日曜日=0) の形式で日付文字列を作成
        date_str = f"{row['年']}-{week_str}-0"
        return pd.to_datetime(date_str, format='%Y-%W-%w') # %W: 月曜始まりの週番号
    except ValueError:
        # 不正な日付形式の場合はNoneを返すなどエラーハンドリング
        return pd.NaT

# CSVファイルの読み込み (Shift-JISエンコーディングを指定)
file_path = 'kansensyo/kansensyo_201501_202504.csv'
try:
    # まずShift-JISで試す
    try:
        df = pd.read_csv(file_path, encoding='shift_jis')
    except UnicodeDecodeError:
        # Shift-JISで失敗した場合はUTF-8で試す
        st.warning("Shift-JISでの読み込みに失敗しました。UTF-8で再試行します。")
        df = pd.read_csv(file_path, encoding='utf-8')
    
    # 日付列を作成
    df['Date'] = df.apply(year_week_to_date, axis=1)
    # Date列がNaTでない行のみを保持
    df = df.dropna(subset=['Date'])
    # Date列をインデックスに設定（任意）
    # df = df.set_index('Date') # Keep Date as a column for filtering

    st.title('東京都 感染症データ ビジュアライゼーション')

    # --- フィルター ---
    st.sidebar.header('フィルター設定') # Move filters to sidebar for better layout

    # 期間選択フィルター
    min_date = df['Date'].min().date()
    max_date = df['Date'].max().date()
    start_date = st.sidebar.date_input('開始日', min_date, min_value=min_date, max_value=max_date)
    end_date = st.sidebar.date_input('終了日', max_date, min_value=start_date, max_value=max_date)

    # 感染症名のリストを取得 (年、週、Dateカラムを除外)
    infection_columns = [col for col in df.columns if col not in ['年', '週', 'Date']]

    # 感染症選択フィルター
    selected_infections = st.sidebar.multiselect(
        '表示したい感染症を選択してください:',
        infection_columns,
        default=infection_columns[0] if infection_columns else None # デフォルトで最初の感染症を選択
    )

    # 選択された期間でデータをフィルタリング
    df_filtered = df[(df['Date'].dt.date >= start_date) & (df['Date'].dt.date <= end_date)]

    # --- メイン表示エリア ---

    # 選択された感染症がある場合のみ表示
    if selected_infections:
        # --- 年別累計感染者数プレビュー ---
        st.header('年別 累計感染者数 (選択期間・感染症)')
        # 選択された感染症と年でグループ化し、合計を計算
        yearly_summary = df_filtered.groupby('年')[selected_infections].sum()
        st.dataframe(yearly_summary)

        # --- サマリー指標 ---
        st.header('サマリー指標 (選択期間)')
        col1, col2, col3 = st.columns(3)

        # 選択された感染症のデータを抽出
        df_selected_filtered = df_filtered[['Date'] + selected_infections]

        if not df_selected_filtered.empty:
            # 最新週の値 (選択期間の最終日を含む週)
            latest_data = df_selected_filtered[df_selected_filtered['Date'] == df_selected_filtered['Date'].max()]
            latest_total = latest_data[selected_infections].sum().sum() # 選択された全感染症の合計
            col1.metric("最新週 合計感染者数", f"{latest_total:,.0f}")

            # 期間内最大値 (選択された全感染症の週ごとの合計の最大値)
            weekly_sum = df_selected_filtered.set_index('Date')[selected_infections].sum(axis=1)
            max_weekly_total = weekly_sum.max()
            col2.metric("期間内 週別最大合計感染者数", f"{max_weekly_total:,.0f}")

            # 期間内合計値
            total_sum = df_selected_filtered[selected_infections].sum().sum()
            col3.metric("期間内 累計感染者数", f"{total_sum:,.0f}")
        else:
            col1.metric("最新週 合計感染者数", "N/A")
            col2.metric("期間内 週別最大合計感染者数", "N/A")
            col3.metric("期間内 累計感染者数", "N/A")


        # --- 時系列グラフ ---
        st.header('感染症の推移')
        # Plotlyで表示するためにデータを整形 (melt) - フィルタリング済みデータを使用
        df_melted = pd.melt(df_selected_filtered, id_vars=['Date'], var_name='感染症名', value_name='感染者数')

        # Plotlyで時系列グラフを作成
        fig = px.line(df_melted, x='Date', y='感染者数', color='感染症名',
                      title='選択された感染症の週別感染者数推移')
        fig.update_layout(xaxis_title='日付', yaxis_title='感染者数')
        st.plotly_chart(fig, use_container_width=True)

    else:
        st.warning('感染症を選択してください。')


    # 今後のステップのためのコメント
    # TODO: 下段に補足情報や別グラフを追加 (オプション)

except FileNotFoundError:
    st.error(f"エラー: ファイルが見つかりません - {file_path}")
except Exception as e:
    st.error(f"データの読み込み中にエラーが発生しました: {e}")
