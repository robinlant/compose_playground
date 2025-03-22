from dataclasses import dataclass
from datetime import datetime

@dataclass
class VoteEntity:
    id: int
    user_id: int
    option_id: int
    vote_date: datetime

@dataclass
class OptionEntity:
    id: int
    poll_id: int
    text: str

@dataclass
class PollEntity:
    id: int
    name: str
    tag: str
    user_id: int
    creation_date: datetime
    anonymous_voting: bool
    multiple_choice: bool
    options: list[OptionEntity] | None = None

@dataclass
class UserEntity:
    id: int
    name: str
    password_hash: str
    created_polls: list[PollEntity] | None = None