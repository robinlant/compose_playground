from datetime import datetime
from typing import Any

from psycopg2._psycopg import cursor
from psycopg2.errors import UniqueViolation, ForeignKeyViolation
from psycopg2.extras import execute_values

from .dal_entities import UserEntity, PollEntity, OptionEntity, VoteEntity
from .exceptions import DalUniqueViolationException, DalForeignKeyViolationException, DalUnexpectedError, DalNotFound


class GenericRepository:
    def __init__(self, crs: cursor):
        self.cur = crs

    def commit(self) -> None:
        self.cur.connection.commit()


class UserRepository(GenericRepository):
    def __init__(self, crs: cursor):
        super().__init__(crs)

    def update_user(self, user: UserEntity) -> None:
        found_user = self.get_user_by_id(user_id=user.id)
        _ensure_found(found_user, table_name="users", column_name="id", identifier=user.id)
        self.cur.execute("""
        UPDATE users
        SET name = %s, password_hash = %s
        WHERE id = %s;
        """, (user.name, user.password_hash, user.id))

    def create_user(self, name: str, password_hash: str, commit: bool = True) -> None:
        try:
            self.cur.execute("""
                INSERT INTO users
                (name, password_hash)
                VALUES (%s, %s)
                """, (name, password_hash))
        except UniqueViolation:
            raise DalUniqueViolationException("users", "name", name)

        if commit:
            self.commit()

    def get_users(self, user_ids: list[int] | None = None) -> list[UserEntity]:
        if user_ids is None:
            self.cur.execute("""
            SELECT id, name, password_hash FROM users;
            """)
        else:
            self.cur.execute("""
            SELECT id, name, password_hash FROM users
            WHERE id IN %s;
            """, (tuple(user_ids),))
        rows = self.cur.fetchall()
        return [UserEntity(id=row[0], name=row[1], password_hash=row[2]) for row in rows]

    def delete_user(self, user_id: int, commit: bool = True) -> None:
        self.cur.execute("""
        DELETE FROM users
        WHERE id = %s;
        """, (user_id,))
        if commit:
            self.commit()

    def get_user_by_id(self, user_id: int) -> UserEntity | None:
        self.cur.execute("""
        SELECT id, name, password_hash FROM users
        WHERE id = %s;
        """, (user_id,))
        return self._fetch_user()

    def get_user_by_name(self, name: str) -> UserEntity | None:
        self.cur.execute("""
        SELECT id, name, password_hash FROM users
        WHERE name = %s;
        """, (name,))
        return self._fetch_user()

    def _fetch_user(self) -> UserEntity | None:
        rows = self.cur.fetchmany(1)
        if len(rows) == 0:
            return None
        row = rows[0]
        return UserEntity(id=row[0], name=row[1], password_hash=row[2])


class PollRepository(GenericRepository):
    def __init__(self, crs: cursor):
        super().__init__(crs)

    def create_poll(self, name: str, tag: str, user_id: int, anonymous_voting: bool, multiple_choice: bool,
                    options: list[str], commit: bool = True) -> None:
        try:
            self.cur.execute("""
            INSERT INTO polls
            (name, tag, user_id, anonymous_voting, multiple_choice)
            values (%s, %s, %s, %s, %s);
            """, (name, tag, user_id, anonymous_voting, multiple_choice))

            poll = self.get_poll_by_user_and_tag(user_id, tag)
            if poll is None:
                raise DalUnexpectedError("Data Corruption, Poll was not found")

            options_data = [(opt, poll.id) for opt in options]
            execute_values(self.cur, """
            INSERT INTO options
            (text, poll_id)
            values %s;
            """, options_data)

        except ForeignKeyViolation:
            raise DalForeignKeyViolationException("polls", "user_id", user_id)
        except UniqueViolation:
            raise DalUniqueViolationException("polls", "tag", tag)
        if commit:
            self.commit()

    def get_polls(self, poll_ids: list[int] | None = None) -> list[PollEntity]:
        if poll_ids is None:
            self.cur.execute("""
            SELECT id, name, tag, user_id, anonymous_voting, multiple_choice, creation_date
            FROM polls;
            """)
        else:
            self.cur.execute("""
            SELECT id, name, tag, user_id, anonymous_voting, multiple_choice, creation_date
            FROM polls
            WHERE id IN %s;
            """, (tuple(poll_ids),))
        return self._fetch_polls()

    def get_poll_by_id(self, poll_id: int) -> PollEntity | None:
        self.cur.execute("""
        SELECT id, name, tag, user_id, anonymous_voting, multiple_choice, creation_date
        FROM polls
        WHERE id = %s;
        """, (poll_id,))
        return self._fetch_poll()

    def get_polls_by_user(self, user_id: int) -> list[PollEntity]:
        self.cur.execute("""
        SELECT id, name, tag, user_id, anonymous_voting, multiple_choice
        FROM polls
        WHERE user_id = %s;
        """, (user_id,))
        return self._fetch_polls()

    def get_poll_by_user_and_tag(self, user_id: int, tag: str) -> PollEntity | None:
        self.cur.execute("""
        SELECT id, name, tag, user_id, anonymous_voting, multiple_choice, creation_date
        FROM polls
        WHERE tag = %s AND user_id = %s;
        """, (tag, user_id))
        return self._fetch_poll()

    def delete_poll(self, poll_id: int, commit: bool = True) -> None:
        self.cur.execute("""
        DELETE FROM polls
        WHERE id = %s;
        """, (poll_id,))

        if commit:
            self.commit()

    def get_options_for_poll(self, poll_id: int | PollEntity) -> list[OptionEntity]:
        if isinstance(poll_id, PollEntity):
            poll_id = poll_id.id

        self.cur.execute("""
        SELECT id, text
        FROM options
        WHERE poll_id = %s;
        """, (poll_id,))

        rows = self.cur.fetchall()
        return [OptionEntity(id=row[0], text=row[1], poll_id=poll_id) for row in rows]

    def get_option_by_id(self, option_id: int) -> OptionEntity | None:
        self.cur.execute("""
        SELECT id, text, poll_id
        FROM options
        WHERE id = %s;
        """, (option_id,))
        row = self.cur.fetchone()
        if row is None:
            return None
        return OptionEntity(id=row[0], text=row[1], poll_id=row[2])

    def _fetch_polls(self) -> list[PollEntity]:
        rows = self.cur.fetchall()
        return [self._to_poll(row) for row in rows]

    def _fetch_poll(self) -> None | PollEntity:
        row = self.cur.fetchone()
        if row is None:
            return None
        return self._to_poll(row)

    @staticmethod
    def _to_poll(data: tuple[int, str, str, int, bool, bool, datetime]) -> PollEntity:
        return PollEntity(id=data[0], name=data[1], tag=data[2], user_id=data[3], anonymous_voting=data[4],
                          multiple_choice=data[5], creation_date=data[6])


class VoteRepository(GenericRepository):
    def __init__(self, crs: cursor, user_repository: UserRepository, poll_repository: PollRepository):
        self.user_repository = user_repository
        self.poll_repository = poll_repository
        super().__init__(crs)

    def create_vote(self, option_id: int, user_id: int, commit: bool = True):

        user = self.user_repository.get_user_by_id(user_id)
        option = self.poll_repository.get_option_by_id(option_id)
        _ensure_found(user, table_name="users", column_name="id", identifier=user_id)
        _ensure_found(option, table_name="options", column_name="id", identifier=option_id)

        self.cur.execute("""
        INSERT INTO votes
        (user_id, option_id)
        values (%s, %s);
        """, (user_id, option_id))

        if commit:
            self.commit()

    def delete_vote(self, vote_id: int, commit: bool = True) -> None:
        self.cur.execute("""
        DELETE FROM votes
        WHERE id = %s;
        """, (vote_id,))

        if commit:
            self.commit()

    def get_vote_by_id(self, vote_id: int) -> VoteEntity | None:
        self.cur.execute("""
        SELECT id, user_id, option_id, vote_date FROM votes
        WHERE id = %s;        
        """, (vote_id,))

        return self.fetch_vote()

    def get_votes_by_poll(self, poll_id: int) -> list[VoteEntity]:
        self.cur.execute("""
        SELECT votes.id, votes.user_id, votes.option_id, votes.vote_date FROM votes
        LEFT JOIN options
        ON votes.option_id = options.id
        WHERE options.poll_id = %s;
        """, (poll_id,))

        return self.fetch_votes()

    def get_votes_by_user(self, user_id: int) -> list[VoteEntity]:
        self.cur.execute("""
        SELECT id, user_id, option_id, vote_date FROM votes
        WHERE user_id = %s;
        """, (user_id,))

        return self.fetch_votes()

    def get_votes_by_user_poll(self, poll_id: int, user_id: int) -> list[VoteEntity]:
        self.cur.execute("""
        SELECT votes.id, votes.user_id, votes.option_id, votes.vote_date FROM votes
        LEFT JOIN options
        ON votes.option_id = options.id
        WHERE options.poll_id = %s AND votes.user_id = %s;
        """, (poll_id, user_id))

        return self.fetch_votes()

    def fetch_votes(self) -> list[VoteEntity]:
        rows = self.cur.fetchall()
        return [self._to_vote(row) for row in rows]

    def fetch_vote(self) -> VoteEntity | None:
        row = self.cur.fetchone()
        if row is None:
            return None
        return self._to_vote(row)

    @staticmethod
    def _to_vote(data: tuple[int, int, int, datetime]) -> VoteEntity:
        return VoteEntity(id=data[0], user_id=data[1], option_id=data[2], vote_date=data[3])


def _ensure_found(obj: Any, table_name: str, column_name: str, identifier: str | int) -> None:
    if obj is None:
        raise DalNotFound(table_name, column_name, identifier)
