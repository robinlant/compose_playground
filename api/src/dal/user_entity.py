from dataclasses import dataclass

@dataclass
class UserEntity:
    id: int
    name: str
    password: str