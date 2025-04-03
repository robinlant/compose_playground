import pytest
from fastapi.exceptions import HTTPException

from src.view.error_or import ErrorOr


def test_error_or_no_error_return_obj():
    # Act
    obj = ErrorOr("some_value")
    res = obj.return_or_raise_http_exception()

    # Assert
    assert obj.is_error is False
    assert obj.obj == "some_value"
    assert res == "some_value"


def test_error_or_error_obj_none():
    # Act
    obj = ErrorOr(is_error=True, error_msg="error_happened", error_code=102)
    exc: HTTPException
    with pytest.raises(HTTPException) as e:
        obj.return_or_raise_http_exception()

    # Assert
    assert obj.is_error is True
    assert obj.obj is None
    assert obj.error_code == 102
    assert obj.error_msg == "error_happened"
    assert e.value.status_code == 102


def test_error_or_error_no_exit_code_given_raise_exception():
    # Act & Assert
    with pytest.raises(ValueError):
        obj = ErrorOr(is_error=True, error_msg="error_happened")
