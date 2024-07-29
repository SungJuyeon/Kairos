import requests
import arrow
import os
from dotenv import load_dotenv

# 환경 변수 파일(.env) 로드
load_dotenv()

# 환경 변수에서 서비스 키를 가져옴
SERVICE_KEY = os.getenv("WEATHER_KEY")
api_url = "http://apis.data.go.kr/1360000/VilageFcstInfoService_2.0/getVilageFcst"

# 관측 위치 좌표 (서울 강남구 개포2동)
location_params = {
    'nx': '55',
    'ny': '127',
}

# 예보 항목 코드와 설명
forecast_categories = {
    'SKY': '하늘 상태',
    'PTY': '강수 형태',
    'TMN': '최저 기온',
    'TMX': '최고 기온'
}

# 하늘 상태 코드와 설명 매핑
STATUS_OF_SKY = {
    '1': '맑습니다.',
    '3': '구름이 많습니다.',
    '4': '흐립니다.'
}

# 강수 형태 코드와 설명 매핑
STATUS_OF_PRECIPITATION = {
    '0': '없음',
    '1': '비',
    '2': '비/눈',
    '3': '눈'
}

def fetch_data_from_kma(current_time_kst, category, fcst_time, forecast_day):
    """
    기상청 API를 통해 특정 시간의 예보 데이터를 가져오는 함수.
    :param current_time_kst: 현재 KST(한국 표준시) 시간 (arrow 객체)
    :param category: 예보 항목 코드 (예: 'SKY', 'PTY')
    :param fcst_time: 예보 시간 (예: '0800')
    :param forecast_day: 예보 일수 (0: 오늘, 1: 내일, 2: 모레)
    :return: 예보 값 또는 None (예보 값을 찾지 못한 경우)
    """
    try:
        date_format = "YYYYMMDD"
        base_date = arrow.now('Asia/Seoul').format(date_format)  # 기준 날짜를 현재 날짜로 설정
        fcst_date = current_time_kst.shift(days=forecast_day).format(date_format)  # 예보 날짜 설정
        page_no = 1
        num_of_rows = 100  # 한 번에 가져올 데이터 수를 100으로 설정

        while True:
            # API 요청에 필요한 매개변수 설정
            params = {
                'serviceKey': SERVICE_KEY,
                'numOfRows': num_of_rows,
                'dataType': 'JSON',
                'base_time': '0200',  # 기준 시간을 0200으로 고정
                'nx': location_params['nx'],
                'ny': location_params['ny'],
                'base_date': base_date,
                'pageNo': page_no
            }

            # API 요청 보내기
            response = requests.get(api_url, params=params)
            response.raise_for_status()  # HTTP 오류 발생 시 예외 발생
            data = response.json()

            # 응답 데이터에서 필요한 정보를 찾음
            items = data.get('response', {}).get('body', {}).get('items', {}).get('item', [])
            found = next((item for item in items if item['category'] == category and item['fcstTime'] == fcst_time and item['fcstDate'] == fcst_date), None)

            if found:
                return found['fcstValue']

            if len(items) < num_of_rows:    # 끝까지 읽음
                break
            page_no += 1

    except requests.exceptions.RequestException as err:
        print(f"Error: {err}")

    return None  # 예보 값을 찾지 못하면 반환

def get_weather_info(forecast_day=0):
    """
    특정 날짜의 예보 데이터를 기반으로 날씨 정보를 구성하는 함수.
    :param forecast_day: 예보 일수 (0: 오늘, 1: 내일, 2: 모레)
    :return: 날씨 정보 문자열
    """
    current_time_kst = arrow.now('Asia/Seoul')  # 현재 KST(한국 표준시) 시간
    date_format = "YYYY년 MM월 DD일 dddd"
    date_of_today = current_time_kst.shift(days=forecast_day).format(date_format, locale="ko_kr")  # 날짜를 한국어 형식으로 포맷

    # 날씨 정보 초기화
    weather_msg = ""
    sky = fetch_data_from_kma(current_time_kst, 'SKY', '0800', forecast_day)  # 하늘 상태 예보 값 가져오기
    precipitation = fetch_data_from_kma(current_time_kst, 'PTY', '0800', forecast_day)  # 강수 형태 예보 값 가져오기
    lowest_temp_of_today = fetch_data_from_kma(current_time_kst, 'TMN', '0600', forecast_day)  # 최저 기온 예보 값 가져오기
    highest_temp_of_today = fetch_data_from_kma(current_time_kst, 'TMX', '1500', forecast_day)  # 최고 기온 예보 값 가져오기

    if (sky is None or precipitation is None or
            lowest_temp_of_today is None or highest_temp_of_today is None):
        weather_msg = "날씨 정보를 가져오지 못했습니다."  # 예보 값을 가져오지 못한 경우 메시지
    else:
        # 하늘 상태에 따른 날씨 설명
        weather_of_today = STATUS_OF_SKY.get(sky, '알 수 없음')

        # 강수 형태에 따른 추가 메시지
        if precipitation == '1':
            weather_of_today += "\n비가 내릴 예정이니 우산을 챙기세요."
        elif precipitation == '2':
            weather_of_today += "\n비 또는 눈이 내릴 예정이니 우산을 챙기세요."
        elif precipitation == '3':
            weather_of_today += "\n눈이 내릴 예정이니 우산을 챙기세요."
        else:
            weather_of_today += "\n강수: 없음"

        # 최종 날씨 정보 메시지 구성
        weather_msg = (
            f"{date_of_today} 날씨를 알려드리겠습니다.\n"
            f"현재 날씨는 {weather_of_today}\n"
            f"최고 기온은 {highest_temp_of_today}도 입니다.\n"
            f"최저 기온은 {lowest_temp_of_today}도 입니다.\n"
        )

    return weather_msg

if __name__ == "__main__":
    # 날씨 정보를 가져와 출력
    weather_info = get_weather_info()
    print(weather_info)

    # print(get_weather_info(0))  # 오늘
    # print(get_weather_info(1))  # 내일
    # print(get_weather_info(2))  # 모레
