from enum import Enum
from fastapi import status


class ErrorCode(Enum):
    # 400 : 요청 오류
    BAD_REQUEST = (status.HTTP_400_BAD_REQUEST, "ERR_COMMON_4000", "잘못된 요청입니다.")
    UNAUTHORIZED = (status.HTTP_401_UNAUTHORIZED, "ERR_COMMON_4001", "로그인 인증이 필요합니다.")
    FORBIDDEN = (status.HTTP_403_FORBIDDEN, "ERR_COMMON_4002", "접근 권한이 없는 요청입니다.")
    NOT_FOUND = (status.HTTP_404_NOT_FOUND, "ERR_COMMON_4003", "값을 불러오는데 실패하였습니다.")
    INVALID_INPUT = (status.HTTP_400_BAD_REQUEST, "ERR_COMMON_4004", "입력값이 올바르지 않습니다.")

    # 사용자 관련 오류
    USER_INVALID = (status.HTTP_400_BAD_REQUEST, "ERR_USER_4000", "올바르지 않은 아이디입니다.")

    def __init__(self, http_status: int, code: str, message: str):
        self.http_status = http_status
        self.code = code
        self.message = message

    @property
    def details(self):
        """ErrorCode의 상세 정보 반환"""
        return {
            "http_status": self.http_status,
            "code": self.code,
            "message": self.message
        }
