class NotFoundException(BaseException):
    def __init__(self, type: type, entity_id: int):
        self.msg = f"{type} was not found, id: {entity_id}"
        super().__init__(self.msg)


class DalUniqueViolationException(BaseException):
    def __init__(
        self, table_name: str, columnn_name: str, identifier: str | int
    ):
        self.msg = f"Unique constraint violation: {table_name}:{columnn_name}:{identifier}"
        super().__init__(self.msg)


class DalForeignKeyViolationException(BaseException):
    def __init__(
        self, table_name: str, column_name: str, identifier: str | int
    ):
        self.msg = f"Foreign constraint violation: {table_name}:{column_name}:{identifier}"
        super().__init__(self.msg)


class DalUnexpectedError(BaseException):
    def __init__(self, msg: str):
        self.msg = msg
        super().__init__(self.msg)


class DalNotFound(BaseException):
    def __init__(
        self, table_name: str, columnn_name: str, identifier: str | int
    ):
        self.msg = f"Not found: {table_name}:{columnn_name}:{identifier}"
        super().__init__(self.msg)
