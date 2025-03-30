class UserExistsException(BaseException):
    def __init__(self, name: str):
        self.msg = f"User already exists: {name}"
        super().__init__(self.msg)


class PollExistsException(BaseException):
    def __init__(self, tag: str, user_id: int):
        self.msg = f"Poll already exists for given user {user_id}: {tag}"
        super().__init__(self.msg)


class NotFound(BaseException):
    def __init__(self, model_name: str, identificator: int | str):
        self.msg = f"{model_name} not found: {identificator}"


class DatabaseExcetpion(BaseException):
    def __init__(self, msg: str):
        self.msg = msg
        super().__init__(self.msg)


class NotAllowed(BaseException):
    def __init__(self, msg: str):
        self.msg = msg
        super().__init__(self.msg)


class UnallowedCharactersException(BaseException):
    def __init__(self, msg: str, string: str):
        self.msg = f"Unallowed characters in: {string}. Message: {msg}"
        super().__init__(self.msg)


class FalseStringFormatException(BaseException):
    def __init__(self, msg: str, string: str):
        self.msg = f"False string format: {string}. Message: {msg}"
        super().__init__(self.msg)


class ModelNotFound(BaseException):
    def __init__(self, msg: str):
        self.msg = msg
        super().__init__(self.msg)


class WrongCredentialsException(BaseException):
    def __init__(self, msg: str):
        self.msg = msg
        super().__init__(self.msg)
