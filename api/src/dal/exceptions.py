class NotFoundException(BaseException):
    def __init__(self, type: type, entity_id: int):
        self.msg = f"{type} was not found, id: {entity_id}"
        super().__init__(self.msg)