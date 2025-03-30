from src.bll.bll_exceptions import NotFound, NotAllowed, PollExistsException, DatabaseExcetpion
from src.bll.bll_models import PollModel, OptionModel
from src.dal import PollEntity
from src.dal.dal_entities import OptionEntity
from src.dal.exceptions import DalUniqueViolationException
from src.dal.repositories import PollRepository, VoteRepository


class PollService:
    def __init__(self, poll_repository: PollRepository, vote_repository: VoteRepository):
        self.poll_repository = poll_repository
        self.vote_repository = vote_repository

    def get_polls_by_userid(self, user_id: int) -> list[PollModel]:
        polls_entities = self.poll_repository.get_polls_by_user(user_id=user_id)
        poll_models = list()
        for poll in polls_entities:
            options = self.poll_repository.get_options_for_poll(poll_id=poll.id)
            poll_models.append(self._to_poll_model(poll, options))
        return poll_models

    def get_poll_by_id(self, poll_id: int) -> PollModel | None:
        poll_entity = self.poll_repository.get_poll_by_id(poll_id=poll_id)
        if poll_entity is None:
            return None
        return self._get_poll(poll_entity)

    def get_poll_by_tag_userid(self, tag: str, user_id: int) -> PollModel | None:
        poll_entity = self.poll_repository.get_poll_by_user_and_tag(tag=tag, user_id=user_id)
        if poll_entity is None:
            return None
        return self._get_poll(poll_entity)

    def create_poll(
            self,
            name: str,
            tag: str,
            anonymous_voting: bool,
            multiple_choice: bool,
            options: list[str],
            user_id: int
    ) -> PollModel:
        try:
            self.poll_repository.create_poll(
                name=name,
                tag=tag,
                user_id=user_id,
                anonymous_voting=anonymous_voting,
                multiple_choice=multiple_choice,
                options=options
            )
        except DalUniqueViolationException:
            raise PollExistsException(tag=tag, user_id=user_id)

        poll = self.get_poll_by_tag_userid(tag=tag, user_id=user_id)

        if poll is None:
            raise DatabaseExcetpion("Database error. Please try again")

        return poll

    def delete_poll_by_id(self, poll_id, user_id: int) -> None:
        poll = self.poll_repository.get_poll_by_id(poll_id=poll_id)

        if poll is None:
            raise NotFound("poll", poll_id)
        if poll.user_id != user_id:
            raise NotAllowed(f"User {user_id} doesn't own poll {poll_id}")

        self.poll_repository.delete_poll(poll_id=poll_id)

    def _get_poll(self, poll_entity: PollEntity) -> PollModel:
        options = self.poll_repository.get_options_for_poll(poll_id=poll_entity.id)
        return self._to_poll_model(poll_entity, options)

    def _to_poll_model(self, poll_entity: PollEntity, option_entities: list[OptionEntity] | None) -> PollModel:
        poll = PollModel(
            id=poll_entity.id,
            user_id=poll_entity.user_id,
            name=poll_entity.name,
            tag=poll_entity.tag,
            creation_date=poll_entity.creation_date,
            anonymous_voting=poll_entity.anonymous_voting,
            multiple_choice=poll_entity.multiple_choice
        )

        poll.options = [self._to_option_model(opt) for opt in option_entities]

        return poll

    @staticmethod
    def _to_option_model(option_entity: OptionEntity) -> OptionModel:
        return OptionModel(
            id=option_entity.id,
            text=option_entity.text
        )
