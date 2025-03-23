from typing import TypeVar

from fastapi.exceptions import HTTPException

T = TypeVar("T")


class ErrorOr[T]:
    def __init__(self, obj: T | None = None, is_error: bool = False, error_msg: str | None = None,
                 error_code: int | None = None):
        if is_error and error_code is None:
            raise ValueError("error code cannot be None")
        self.is_error = is_error
        self.error_msg = error_msg
        self.error_code = error_code
        self.obj = obj

    def return_or_raise_http_exception(self) -> T:
        if self.is_error:
            raise HTTPException(status_code=self.error_code, detail=self.error_msg)
        return self.obj
