from datetime import datetime
from unittest.mock import MagicMock

import pytest
from pytest import fixture

from src.bll.bll_exceptions import PollExistsException, NotFound, NotAllowed
from src.bll.bll_models import PollModel, OptionModel
from src.bll.poll_service import PollService
from src.dal import PollEntity, VoteRepository, PollRepository
from src.dal.dal_entities import OptionEntity
from src.dal.exceptions import DalUniqueViolationException


@fixture
def poll_entity() -> PollEntity:
    return PollEntity(
        id=1,
        name="Somename",
        tag="sometag",
        user_id=1,
        creation_date=datetime.now(),
        anonymous_voting=False,
        multiple_choice=False,
    )


@fixture
def option_entities() -> list[OptionEntity]:
    return [OptionEntity(id=i, poll_id=1, text=f"sometext {i}") for i in range(5)]


@fixture
def vote_repository() -> VoteRepository:
    return MagicMock(spec=VoteRepository)


@fixture
def poll_repository() -> PollRepository:
    return MagicMock(spec=PollRepository)


def assert_poll_entity_to_poll_model(
    poll_entity: PollEntity, poll_model: PollModel
) -> None:
    assert poll_entity.name == poll_model.name
    assert poll_entity.tag == poll_model.tag
    assert poll_entity.creation_date == poll_model.creation_date
    assert poll_entity.anonymous_voting == poll_model.anonymous_voting
    assert poll_entity.multiple_choice == poll_model.multiple_choice
    assert poll_entity.user_id == poll_model.user_id


def assert_option_entity_to_entity_model(
    option_entity: OptionEntity, option_model: OptionModel
):
    assert option_entity.id == option_model.id
    assert option_entity.text == option_model.text


def test_get_polls_by_userid_returns_polls(
    poll_repository: PollRepository | MagicMock,
    vote_repository: VoteRepository | MagicMock,
    poll_entity: PollEntity,
    option_entities: list[OptionEntity],
):
    # Arrange
    poll_repository.get_options_for_poll.return_value = option_entities
    poll_repository.get_polls_by_user.return_value = [poll_entity]

    # Act
    poll_service = PollService(
        poll_repository=poll_repository, vote_repository=vote_repository
    )
    poll = poll_service.get_polls_by_userid(user_id=1)[0]

    # Assert
    poll_repository.get_polls_by_user.assert_called_with(user_id=1)
    poll_repository.get_options_for_poll.assert_called_with(poll_id=poll_entity.id)
    assert_poll_entity_to_poll_model(poll_entity=poll_entity, poll_model=poll)
    for ent, model in zip(option_entities, poll.options):
        assert_option_entity_to_entity_model(option_entity=ent, option_model=model)


def test_get_poll_by_id_returns_poll(
    poll_repository: PollRepository | MagicMock,
    vote_repository: VoteRepository | MagicMock,
    poll_entity: PollEntity,
    option_entities: list[OptionEntity],
):
    # Arrange
    poll_repository.get_options_for_poll.return_value = option_entities
    poll_repository.get_poll_by_id.return_value = poll_entity

    # Act
    poll_service = PollService(
        poll_repository=poll_repository, vote_repository=vote_repository
    )
    poll = poll_service.get_poll_by_id(poll_id=poll_entity.id)

    # Assert
    poll_repository.get_poll_by_id.assert_called_with(poll_id=1)
    poll_repository.get_options_for_poll.assert_called_with(poll_id=poll_entity.id)
    assert_poll_entity_to_poll_model(poll_entity=poll_entity, poll_model=poll)
    for ent, model in zip(option_entities, poll.options):
        assert_option_entity_to_entity_model(option_entity=ent, option_model=model)


def test_get_poll_by_userid_tag_returns_polls(
    poll_repository: PollRepository | MagicMock,
    vote_repository: VoteRepository | MagicMock,
    poll_entity: PollEntity,
    option_entities: list[OptionEntity],
):
    # Arrange
    poll_repository.get_options_for_poll.return_value = option_entities
    poll_repository.get_poll_by_user_and_tag.return_value = poll_entity

    # Act
    poll_service = PollService(
        poll_repository=poll_repository, vote_repository=vote_repository
    )
    poll = poll_service.get_poll_by_tag_userid(tag=poll_entity.tag, user_id=1)

    # Assert
    poll_repository.get_poll_by_id.get_poll_by_user_and_tag(poll_id=1)
    poll_repository.get_options_for_poll.assert_called_with(poll_id=poll_entity.id)
    assert_poll_entity_to_poll_model(poll_entity=poll_entity, poll_model=poll)
    for ent, model in zip(option_entities, poll.options):
        assert_option_entity_to_entity_model(option_entity=ent, option_model=model)


def test_create_poll_poll_exists_raise_exception(
    poll_repository: PollRepository | MagicMock,
    vote_repository: VoteRepository | MagicMock,
    poll_entity: PollEntity,
):
    # Arrange
    poll_repository.create_poll.side_effect = DalUniqueViolationException("", "", "")

    # Act & Assert
    poll_service = PollService(
        poll_repository=poll_repository, vote_repository=vote_repository
    )
    with pytest.raises(PollExistsException):
        poll_service.create_poll(
            name=poll_entity.name,
            tag=poll_entity.tag,
            user_id=poll_entity.user_id,
            anonymous_voting=poll_entity.anonymous_voting,
            multiple_choice=poll_entity.multiple_choice,
            options=[],
        )


def test_create_poll_poll_not_exists_returns_poll(
    poll_repository: PollRepository | MagicMock,
    vote_repository: VoteRepository | MagicMock,
    poll_entity: PollEntity,
    option_entities: list[OptionEntity],
):
    # Arrange
    poll_repository.create_poll.return_value = None
    poll_repository.get_poll_by_user_and_tag.return_value = poll_entity
    poll_repository.get_options_for_poll.return_value = option_entities

    # Act
    poll_service = PollService(
        poll_repository=poll_repository, vote_repository=vote_repository
    )
    poll_model = poll_service.create_poll(
        name=poll_entity.name,
        tag=poll_entity.tag,
        user_id=poll_entity.user_id,
        anonymous_voting=poll_entity.anonymous_voting,
        multiple_choice=poll_entity.multiple_choice,
        options=[opt.text for opt in option_entities],
    )

    # Assert
    assert_poll_entity_to_poll_model(poll_entity, poll_model)
    for opt, model in zip(option_entities, poll_model.options):
        assert_option_entity_to_entity_model(option_entity=opt, option_model=model)
    poll_repository.create_poll.assert_called_once_with(
        name=poll_entity.name,
        tag=poll_entity.tag,
        user_id=poll_entity.user_id,
        anonymous_voting=poll_entity.anonymous_voting,
        multiple_choice=poll_entity.multiple_choice,
        options=[opt.text for opt in option_entities],
    )


def test_delete_poll_poll_not_found_raises_exception(
    poll_repository: PollRepository | MagicMock,
    vote_repository: VoteRepository | MagicMock,
):
    # Arrange
    poll_repository.get_poll_by_id.return_value = None

    # Act
    poll_service = PollService(
        poll_repository=poll_repository, vote_repository=vote_repository
    )
    with pytest.raises(NotFound):
        poll_service.delete_poll_by_id(user_id=1, poll_id=1)

    # Assert
    poll_repository.delete_poll.assert_not_called()


def test_delete_poll_poll_exists_returns_none(
    poll_repository: PollRepository | MagicMock,
    vote_repository: VoteRepository | MagicMock,
    poll_entity: PollEntity,
):
    # Arrange
    poll_repository.get_poll_by_id.return_value = poll_entity

    # Act
    poll_service = PollService(
        poll_repository=poll_repository, vote_repository=vote_repository
    )
    poll_service.delete_poll_by_id(user_id=poll_entity.user_id, poll_id=poll_entity.id)

    # Assert
    poll_repository.delete_poll.assert_called_with(poll_id=poll_entity.id)


def test_delete_poll_user_doesnt_own_poll_raises_exception(
    poll_repository: PollRepository | MagicMock,
    vote_repository: VoteRepository | MagicMock,
    poll_entity: PollEntity,
):
    # Arrange
    poll_repository.get_poll_by_id.return_value = poll_entity

    # Act
    poll_service = PollService(
        poll_repository=poll_repository, vote_repository=vote_repository
    )
    with pytest.raises(NotAllowed):
        poll_service.delete_poll_by_id(user_id=100, poll_id=1)

    # Assert
    poll_repository.delete_poll.assert_not_called()
