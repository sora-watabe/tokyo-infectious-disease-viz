# 東京都感染症データビジュアライゼーション

https://sora-watabe.github.io/tokyo-infectious-disease-viz/


Uploading demo.mp4…



このプロジェクトは、東京都の感染症データを可視化するためのStreamlitアプリケーションです。

## 機能

- 感染症データの年別累計表示
- 複数の感染症を選択して時系列グラフで比較
- 期間選択フィルター
- サマリー指標（最新週の感染者数、期間内最大値、期間内合計値）

## 使用方法

1. リポジトリをクローンします。
   ```
   git clone https://github.com/yourusername/tokyo-infectious-disease-viz.git
   cd tokyo-infectious-disease-viz
   ```

2. 必要なライブラリをインストールします。
   ```
   pip install streamlit pandas plotly
   ```

3. アプリケーションを実行します。
   ```
   streamlit run app.py
   ```

4. ブラウザで表示されるURLにアクセスします（通常は http://localhost:8501）。

## データについて

`kansensyo/kansensyo_201501_202504.csv` には、2015年第1週から2025年第15週までの各感染症の週別感染者数が含まれています。

## 今後の開発予定

- 感染者数の予測モデル
- より詳細な地域別データの表示
- 複数の可視化オプションの追加

## ライセンス

このプロジェクトはMITライセンスの下で公開されています。
