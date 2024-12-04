import os
import requests
from dotenv import load_dotenv
from fastapi import HTTPException

load_dotenv()
SPRING_SERVER_URL = os.getenv('SPRING_SERVER_URL')


class UserService:
    @staticmethod
    def get_user_info(token: str):
        try:
            # Authorization 헤더에 Bearer 토큰을 포함
            headers = {
                "Authorization": token  # 헤더에 그대로 전달
            }
            # 스프링 서버로 요청을 보낼 때 헤더에 토큰 포함
            response = requests.get(
                f"{SPRING_SERVER_URL}/users/info",
                headers=headers
            )

            if response.status_code != 200:
                raise HTTPException(status_code=response.status_code, detail="Failed to fetch user info")

            return response.json()
        except requests.exceptions.RequestException as e:
            raise HTTPException(status_code=500, detail=str(e))

    @staticmethod
    def get_user_id(token: str):
        if not token:
            raise HTTPException(status_code=401, detail="Authorization header missing")
        try:
            # UserService를 사용해 사용자 정보 가져오기
            user_info = UserService.get_user_info(token)

            # 사용자 id 추출
            user_id = user_info['result']['id']
            return user_id
        except Exception as e :
            raise HTTPException(status_code=500, detail=str(e))