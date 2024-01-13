import streamlit as st
import requests
import datetime
import json
import matplotlib.pyplot as plt
import numpy as np
import japanize_matplotlib 

# config.jsonから設定を読み込む
with open('config.json', 'r') as f:
  config = json.load(f)

# YouTube Data API v3のAPIキーを設定します
# API_KEY = config['API_KEY']

# streamlit share上でAPIキーを設定する場合
API_KEY = st.secrets['API_KEY']

# チャンネルIDを元にチャンネル情報を取得する関数
def get_channel_info(channel_id):
    url = f'https://www.googleapis.com/youtube/v3/channels?part=snippet,statistics&id={channel_id}&key={API_KEY}'
    response = requests.get(url)
    data = response.json()
    if 'items' in data and len(data['items']) > 0:
        item = data['items'][0]
        channel_title = item['snippet']['title']
        channel_creation_date = item['snippet']['publishedAt']
        total_videos_uploaded = int(item['statistics']['videoCount'])
        subscribers = int(item['statistics']['subscriberCount'])
        return channel_title, channel_creation_date, total_videos_uploaded, subscribers
    else:
        return None, None, None, None

# 検索語句を元にチャンネルを検索し、結果を表示する関数
def search_channels(search_term,max_results=20):
    url = f'https://www.googleapis.com/youtube/v3/search?part=snippet&type=channel&maxResults={max_results}&q={search_term}&key={API_KEY}'
    response = requests.get(url)
    data = response.json()
    channel_data_list = []
    if 'items' in data:
        for item in data['items']:
            channel_id = item['snippet']['channelId']
            channel_title, channel_creation_date, total_videos_uploaded, subscribers = get_channel_info(channel_id)
            if channel_title and channel_creation_date and total_videos_uploaded and subscribers:
                try:
                    channel_creation_date = datetime.datetime.strptime(channel_creation_date, "%Y-%m-%dT%H:%M:%SZ")
                except ValueError:
                    channel_creation_date = datetime.datetime.strptime(channel_creation_date, "%Y-%m-%dT%H:%M:%S.%fZ")
                days_since_channel_creation = (datetime.datetime.now() - channel_creation_date).days
                days_per_video = '{:.2f}'.format(round(days_since_channel_creation / total_videos_uploaded, 2))
                channel_data = {
                    'チャンネル名': channel_title,
                    'チャンネル開設日': channel_creation_date.date(),
                    '投稿動画数': total_videos_uploaded,
                    '運営日数': days_since_channel_creation,
                    '投稿頻度': days_per_video,
                    'チャンネル登録者数': subscribers,
                }
                channel_data_list.append(channel_data)
    channel_data_list.sort(key=lambda x: x['投稿頻度'])
    st.table(channel_data_list)
    # 投稿頻度とチャンネル登録者数の相関を可視化
    post_frequency = [data['投稿頻度'] for data in channel_data_list]
    subscribers = [data['チャンネル登録者数'] for data in channel_data_list]
    channel_names = [data['チャンネル名'] for data in channel_data_list]
    fig, ax1 = plt.subplots()
    color = 'tab:blue'
    ax1.set_xlabel('チャンネル名')
    ax1.set_ylabel('チャンネル登録者数', color=color)
    ax1.plot(channel_names, subscribers, color=color)
    ax1.tick_params(axis='y', labelcolor=color)
    ax2 = ax1.twinx()
    color = 'tab:red'
    ax2.set_ylabel('投稿頻度', color=color)
    ax2.bar(channel_names, post_frequency, color=color, alpha=0.5)
    ax2.tick_params(axis='y', labelcolor=color)
    fig.tight_layout()
    #plt.xticks(rotation=45, ha='right')  # グラフの軸のチャンネル名を縦に表示し、重ならないように調整
    fig.autofmt_xdate(rotation=45, ha='right')
    st.pyplot(fig)
    
# メイン関数
def main():
    st.title('YouTubeチャンネル情報')
    st.markdown('**検索結果は上位20件まで表示**')
    search_term = st.text_input('チャンネルのキーワードを入力してください', '')
    if st.button('チャンネルを検索') and search_term:
        search_channels(search_term)

# メイン関数の実行
if __name__ == "__main__":
    main()