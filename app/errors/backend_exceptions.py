from fastapi import HTTPException

from app.errors.error_codes import ErrorCode
from app.errors.error_dto import ErrorReasonDTO


class BackendException(HTTPException):
    def __init__(self, error_code: ErrorCode):
        """ErrorCode로 초기화된 예외를 생성"""
        self.error_code = error_code
        super().__init__(
            status_code=error_code.http_status,
            detail=ErrorReasonDTO.from_error_code(error_code).dict()
        )
