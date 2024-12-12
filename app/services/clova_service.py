import json
import os

import requests
from fastapi import Response


class ClovaService:
    invoke_url = os.getenv("CLOVA_INVOKE_URL")
    secret_key = os.getenv("CLOVA_SECRETKEY")

    # url 로 직접 요청 (default : sync)
    async def speech_to_text(self, url, callback=None, userdata=None, forbiddens=None, boostings=None,
                             wordAlignment=True, fullText=True):
        request = {
            'url': url,
            'language': 'ko-KR',
            'completion': 'sync',
            'callback': callback,
            'userdata': userdata,
            'wordAlignment': wordAlignment,
            'fullText': fullText,
            'forbiddens': forbiddens,
            'boostings': boostings,
            'diarization': {
                'enable': True,
                'speakerCountMin': -1,
                'speakerCountMax': -1,
            },
        }

        headers = {
            'Accept': 'application/json;UTF-8',
            'Content-Type': 'application/json;UTF-8',
            'X-CLOVASPEECH-API-KEY': self.secret_key
        }

        response = requests.post(headers=headers,
                                 url=self.invoke_url + '/recognizer/url',
                                 data=json.dumps(request).encode('UTF-8'))

        return response.json()

    def speech_to_text_local(self, file):
        request = {
            'language': 'ko-KR',
            'completion': 'sync',
            'diarization': {
                'enable': True,
                'speakerCountMin': -1,
                'speakerCountMax': -1,
            },
        }

        headers = {
            'Accept': 'application/json;UTF-8',
            'X-CLOVASPEECH-API-KEY': self.secret_key
        }

        print(json.dumps(request, ensure_ascii=False).encode('UTF-8'))

        files = {
            'media': open(file, 'rb'),
            'params': (None, json.dumps(request, ensure_ascii=False).encode('UTF-8'), 'application/json')
        }
        response = requests.post(headers=headers, url=self.invoke_url + '/recognizer/upload', files=files)

        return response.json()
