from dataclasses import dataclass
from datetime import datetime


@dataclass
class VoteModel:
    id: int
    user_id: int
    option_id: int
    vote_date: datetime


@dataclass
class OptionModel:
    id: int
    text: str


@dataclass
class PollModel:
    id: int
    name: str
    tag: str
    user_id: int
    creation_date: datetime
    anonymous_voting: bool
    multiple_choice: bool
    options: list[OptionModel] | None = None


@dataclass
class UserModel:
    id: int
    name: str
    created_polls: list[PollModel] | None = None
