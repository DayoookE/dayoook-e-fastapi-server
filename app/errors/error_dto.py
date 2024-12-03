from pydantic import BaseModel

from app.errors.error_codes import ErrorCode


class ErrorReasonDTO(BaseModel):
    code: str
    message: str
    is_success: bool = False
    http_status: int

    @classmethod
    def from_error_code(cls, error_code: ErrorCode):
        """ErrorCode 객체로부터 ErrorReasonDTO 인스턴스를 생성"""
        return cls(
            code=error_code.code,
            message=error_code.message,
            http_status=error_code.http_status,
            is_success=False
        )
