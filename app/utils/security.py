import os
from dotenv import load_dotenv
import jwt
from fastapi import HTTPException, Security, Depends
from fastapi.security import HTTPBearer
from jwt.exceptions import PyJWTError  # JWTError 대신 PyJWTError 사용
import base64

load_dotenv()
SPRING_SERVER_URL = os.getenv('SPRING_SERVER_URL')
JWT_SECURITY_KEY = os.getenv('JWT_SECURITY_KEY')
security = HTTPBearer()


def decode_jwt(token: str):
    try:
        # Base64로 디코딩된 시크릿 키 사용
        decoded_secret = base64.b64decode(JWT_SECURITY_KEY)
        payload = jwt.decode(token, decoded_secret, algorithms=["HS256"])
        return payload
    except PyJWTError as e:
        print(f"JWT 디코딩 에러: {str(e)}")  # 디버깅을 위한 에러 출력
        raise HTTPException(status_code=403, detail="Invalid token")


async def get_current_user(token: str = Security(security)):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_jwt(token.credentials)
        user_id = payload.get("sub")
        if user_id is None:
            raise credentials_exception
        return user_id
    except PyJWTError as e:
        print(f"인증 에러: {str(e)}")  # 디버깅을 위한 에러 출력
        raise credentials_exception