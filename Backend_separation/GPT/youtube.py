import os
import webbrowser
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from dotenv import load_dotenv
import psutil
import time

load_dotenv()
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")

# 전역 변수로 브라우저 프로세스 ID를 저장
browser_process = None

def search_youtube(query):
    try:
        youtube = build("youtube", "v3", developerKey=YOUTUBE_API_KEY)
        request = youtube.search().list(q=query, part="snippet", type="video", maxResults=1)
        response = request.execute()
        video_id = response['items'][0]['id']['videoId']
        return f"https://www.youtube.com/watch?v={video_id}&autoplay=1"
    except HttpError as e:
        print(f"An error occurred: {e}")
        return None

def open_browser(url):
    global browser_process
    if browser_process is None:
        # 첫 번째 노래를 재생할 때 브라우저를 열고 프로세스를 저장
        browser_process = webbrowser.open(url)
    else:
        # 이미 열려 있는 브라우저에서 URL을 변경
        webbrowser.open(url)  # 같은 URL을 다시 열어서 사용자가 직접 탭을 전환하게 함

def close_browser():
    global browser_process
    if browser_process is not None:
        # 브라우저 프로세스 종료
        for proc in psutil.process_iter(['pid', 'name']):
            if proc.info['name'] == 'chrome.exe':
                proc.kill()
        browser_process = None

def play_music_on_youtube(song_name):
    video_url = search_youtube(song_name)
    if video_url:
        open_browser(video_url)
    else:
        print("Unable to retrieve the video URL.")

# if __name__ == "__main__":
#     play_music_on_youtube("뉴진스 하이 보이")
#
#     # 10초 후에 브라우저를 닫도록 설정 (테스트용)
#     time.sleep(10)
#     close_browser()
