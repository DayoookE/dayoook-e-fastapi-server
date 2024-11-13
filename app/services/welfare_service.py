# app/services/welfare_service.py
import requests
import logging
from typing import List, Dict

logger = logging.getLogger(__name__)


class WelfareService:
    def __init__(self):
        self.base_url = "https://m.bokjiro.go.kr"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Origin': 'https://m.bokjiro.go.kr',
            'Referer': 'https://m.bokjiro.go.kr/'
        }
        self.exclude_keywords = ['IBK기업은행', '저출생', '보이는희망']

    async def fetch_welfare_info(self, page: int = 1) -> List[Dict]:
        try:
            url = f"{self.base_url}/ssis-tem/TWAT52005M/twataa/wlfareInfo/selectWlfareInfo.do"
            payload = {
                "dmSearchParam": {
                    "page": str(page),
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

            response = requests.post(url, json=payload, headers=self.headers)
            response.raise_for_status()
            data = response.json()

            welfare_list = []
            for item in data.get('dsServiceList0', []):
                title = item.get('WLFARE_INFO_NM', '')

                if any(keyword in title for keyword in self.exclude_keywords):
                    continue

                welfare_info = {
                    "title": title,
                    "content": item.get('WLFARE_INFO_OUTL_CN', '').strip(),
                    "start_date": item.get('ENFC_BGNG_YMD', ''),
                    "end_date": item.get('ENFC_END_YMD', ''),
                    "organization": item.get('BIZ_CHR_INST_NM', ''),
                    "status": item.get('CVL_PROGRSS_STATUS', ''),
                    "detail_url": f"https://www.bokjiro.go.kr/ssis-tbu/twataa/wlfareInfo/moveTWAT52011M.do?wlfareInfoId={item.get('WLFARE_INFO_ID')}&wlfareInfoReldBztpCd=01"
                }
                welfare_list.append(welfare_info)

            return welfare_list

        except Exception as e:
            logger.error(f"Failed to fetch welfare info: {e}")
            raise Exception(f"Failed to fetch welfare info: {str(e)}")