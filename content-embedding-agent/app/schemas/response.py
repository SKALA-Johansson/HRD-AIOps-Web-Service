from typing import Generic, Optional, TypeVar
from pydantic import BaseModel

T = TypeVar("T")


class ApiResponse(BaseModel, Generic[T]):
    success: bool = True
    code: str
    message: str
    data: Optional[T] = None

    @classmethod
    def ok(cls, data: T, code: str = "COMMON-200", message: str = "요청이 성공했습니다."):
        return cls(success=True, code=code, message=message, data=data)

    @classmethod
    def error(cls, code: str, message: str):
        return cls(success=False, code=code, message=message, data=None)
