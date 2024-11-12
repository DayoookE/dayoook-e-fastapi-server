import requests


def fetch_welfare_info():
    url = "https://m.bokjiro.go.kr/ssis-tem/TWAT52005M/twataa/wlfareInfo/selectWlfareInfo.do"

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Origin': 'https://m.bokjiro.go.kr',
        'Referer': 'https://m.bokjiro.go.kr/'
    }

    payload = {
        "dmSearchParam": {
            "page": "1",
            "onlineYn": "",
            "searchTerm": "",
            "tabId": "1",
            "orderBy": "date",
            "bkjrLftmCycCd": "",
            "daesang": "다문화·탈북민",
            "period": "",
            "age": "",
            "region": "",
            "jjim": "",
            "subject": "",
            "favoriteKeyword": "",
            "endYn": "N",
            "sidoCd": "",
            "sggCd": ""
        },
        "dmScr": {
            "curScrId": "tem/app/twat/twata/twataa/TWAT52005M",
            "befScrId": ""
        }
    }

    # 제외할 키워드 리스트
    exclude_keywords = ['IBK기업은행', '저출생', '보이는희망']

    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        data = response.json()

        print("\n=== 다문화·탈북민 관련 복지 정보 ===\n")

        for item in data.get('dsServiceList0', []):
            title = item.get('WLFARE_INFO_NM', '')

            # 제외할 키워드가 제목에 포함되어 있으면 건너뛰기
            if any(keyword in title for keyword in exclude_keywords):
                continue

            detail_url = (f"https://www.bokjiro.go.kr/ssis-tbu/twataa/wlfareInfo/moveTWAT52011M.do"
                          f"?wlfareInfoId={item.get('WLFARE_INFO_ID')}&wlfareInfoReldBztpCd=01")

            print("-" * 80)
            print(f"제목: {title}")
            print(f"내용: {item.get('WLFARE_INFO_OUTL_CN', '').strip()}")
            print(f"시작일: {item.get('ENFC_BGNG_YMD', '')}")
            print(f"종료일: {item.get('ENFC_END_YMD', '')}")
            print(f"기관: {item.get('BIZ_CHR_INST_NM', '')}")
            print(f"상태: {item.get('CVL_PROGRSS_STATUS', '')}")
            print(f"자세히보기: {detail_url}")
            print("-" * 80)
            print()

    except requests.exceptions.RequestException as e:
        print(f"오류 발생: {str(e)}")


if __name__ == "__main__":
    fetch_welfare_info()