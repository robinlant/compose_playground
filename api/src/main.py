from fastapi import FastAPI, status, HTTPException
from psycopg2 import connect

from dal import (
    NotFoundException,
    InMemoryUserRepository,
    UserEntity,
    ensure_exists,
)
from view import (
    CreateUserDto,
    GetUserDto,
    UpdateUserDto,
    DeleteUserDto,
    ChangePasswordDto,
)
from mapper import to_get_user_dto
from configuration import DB_NAME, DB_USER

app = FastAPI()
db_connection = connect(f"dbname={DB_NAME} user={DB_USER}")
db_cursor = db_connection.cursor()
ensure_exists(db_cursor)
user_repository = InMemoryUserRepository()


@app.get("/")
async def root() -> str:
    return "Hellow Wordle!"


@app.get("/users", status_code=status.HTTP_200_OK)
async def get_all_users() -> list[GetUserDto]:
    global user_repository

    users = []
    for user in user_repository.get_users():
        users.append(to_get_user_dto(user))

    return users


@app.get(
    "/users/{user_id}",
    status_code=status.HTTP_200_OK,
    response_model=GetUserDto,
)
async def get_user(user_id: int) -> GetUserDto:
    global user_repository
    try:
        user = user_repository.get_user(user_id)
        return to_get_user_dto(user)
    except NotFoundException:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)


@app.post(
    "/users", status_code=status.HTTP_201_CREATED, response_model=GetUserDto
)
async def create_user(create_user_dto: CreateUserDto) -> GetUserDto:
    global user_repository

    seeked_user: UserEntity | None = None
    for user in user_repository.get_users():
        if user.name == create_user_dto.name:
            seeked_user = user
            break

    if seeked_user is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"User {seeked_user.name} already exists.",
        )
    else:
        user = user_repository.create_user(
            create_user_dto.name, create_user_dto.password
        )
        return to_get_user_dto(user)


@app.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: int, delete_user_dto: DeleteUserDto) -> None:
    global user_repository

    try:
        user = user_repository.get_user(user_id)
        if user.password_hash != delete_user_dto.password:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
        else:
            user_repository.delete_user(user.id)
            return None
    except NotFoundException:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)


@app.post(
    "/users/{user_id}/change_password", status_code=status.HTTP_204_NO_CONTENT
)
async def change_password(
    user_id: int, change_password_dto: ChangePasswordDto
) -> None:
    global user_repository

    try:
        user = user_repository.get_user(user_id)
        if user.password_hash == change_password_dto.old_password:
            user.password_hash = change_password_dto.new_password
            user_repository.update_user(user)
            return None
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    except NotFoundException:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)


@app.put("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_user(user_id: int, update_user_dto: UpdateUserDto) -> None:
    global user_repository

    try:
        user = user_repository.get_user(user_id)
        if user.password_hash == update_user_dto.password:
            user.name = update_user_dto.name
            user_repository.update_user(user)
            return None
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    except NotFoundException:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
