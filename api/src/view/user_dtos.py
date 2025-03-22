from pydantic import BaseModel

class CreateUserDto(BaseModel):
    name: str
    password: str

class GetUserDto(BaseModel):
    id: int
    name: str
    
class UpdateUserDto(BaseModel):
    name: str
    password: str

class DeleteUserDto(BaseModel):
    password: str
    
class ChangePasswordDto(BaseModel):
    old_password: str
    new_password: str