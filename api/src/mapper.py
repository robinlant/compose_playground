from dal import UserEntity
from api import GetUserDto



def to_get_user_dto(user_entity: UserEntity) -> GetUserDto:
    data = {
        "id": user_entity.id,
        "name": user_entity.name
    }
    user_dto: GetUserDto = GetUserDto(**data)
    return user_dto