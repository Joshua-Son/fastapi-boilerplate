from pydantic import BaseModel

from typing import Optional, Any


class Message(BaseModel):
    message: str

class ResponseBase(BaseModel):
    code: int
    message: str
    data: Optional[Any]

class SuccessResponse(ResponseBase):
    code: int = 200
    message: str = "Operation successful"
    data: Optional[Any] = None

class ErrorResponse(ResponseBase):
    code: int = 400
    message: str = "Operation failed"
    data: Optional[Any] = None