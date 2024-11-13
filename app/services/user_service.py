import os
import requests
from dotenv import load_dotenv
from fastapi import HTTPException

load_dotenv()
SPRING_SERVER_URL = os.getenv('SPRING_SERVER_URL')


class UserService:
    @staticmethod
    def get_user_info_by_email(email: str, token: str):
        try:
            # Authorization 헤더에 Bearer 토큰을 포함
            headers = {
                "Authorization": token  # 헤더에 그대로 전달
            }
            # 스프링 서버로 요청을 보낼 때 헤더에 토큰 포함
            response = requests.get(
                f"{SPRING_SERVER_URL}/users/info?email={email}",
                headers=headers
            )

            if response.status_code != 200:
                raise HTTPException(status_code=response.status_code, detail="Failed to fetch user info")

            return response.json()
        except requests.exceptions.RequestException as e:
            raise HTTPException(status_code=500, detail=str(e))