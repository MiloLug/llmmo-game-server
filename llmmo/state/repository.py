from enum import StrEnum
from functools import cache, wraps
from typing import Callable, Concatenate, Self
from uuid import UUID
from fastmcp import Context
from pydantic import BaseModel, Field
from pathlib import Path

from llmmo.config.settings import config
from llmmo.state.base_manager import BaseManager, BaseObject
from llmmo.utils import json_dumps, json_loads
from llmmo.state.item import Item, ItemManager
from llmmo.state.player import Player, PlayerManager
from llmmo.state.location import Location, LocationManager
from llmmo.state.abstract import Abstract, AbstractManager
from llmmo.state.entity import Entity, EntityManager


# TODO: Later, use sql or mongodb to store the game state.


class ObjectType(StrEnum):
    ITEM = "ITEM"
    LOCATION = "LOCATION"
    ENTITY = "ENTITY"
    ABSTRACT = "ABSTRACT"
    PLAYER = "PLAYER"


class GameState(BaseModel):
    setting: str = ""
    save_summary: str = ""
    locations: dict[UUID, Location] = Field(default_factory=dict)
    players: dict[UUID, Player] = Field(default_factory=dict)
    current_player_id: UUID | None = None
    items: dict[UUID, Item] = Field(default_factory=dict)
    abstracts: dict[UUID, Abstract] = Field(default_factory=dict)
    entities: dict[UUID, Entity] = Field(default_factory=dict)


class GameStateRepository:
    def __init__(self, path: Path):
        self.state = GameState()
        self.path = path

        self.location = LocationManager(self)
        self.player = PlayerManager(self)
        self.item = ItemManager(self)
        self.abstract = AbstractManager(self)
        self.entity = EntityManager(self)

        self._object_registry: dict[ObjectType, BaseManager] = {
            ObjectType.LOCATION: self.location,
            ObjectType.PLAYER: self.player,
            ObjectType.ITEM: self.item,
            ObjectType.ABSTRACT: self.abstract,
            ObjectType.ENTITY: self.entity,
        }

    def get_object(self, object_type: ObjectType, id: UUID) -> BaseObject:
        return self._object_registry[object_type].get(id)

    @classmethod
    @cache
    def for_user(cls, username: str) -> Self:
        return cls(config().db.base_path / username).load()

    def save_game(self, save_summary: str) -> Self:
        self.state.save_summary = save_summary
        self.save()
        return self

    def clear(self) -> Self:
        self.state = GameState()
        self.save()
        return self

    def start_game(
        self,
        setting: str,
        player_name: str,
        location_name: str,
        location_description: str,
    ) -> Self:
        self.clear()
        self.state.setting = setting
        location = self.location.create(
            name=location_name, description=location_description
        )
        self.player.create(
            name=player_name, location_id=location.id, set_as_current=True
        )
        self.save()
        return self

    def load(self) -> Self:
        try:
            with open(self.path, "r") as f:
                self.state = GameState.model_validate(json_loads(f.read()))
        except Exception as e:
            print(f"Error loading game state: {e}. Starting with empty state.")
            self.state = GameState()
        return self

    def save(self) -> Self:
        with open(self.path, "w") as f:
            f.write(json_dumps(self.state.model_dump(mode="json"), indent=True))
        return self


def with_state[**T, R](
    func: Callable[Concatenate[Context, T], R],
) -> Callable[Concatenate[Context, T], R]:
    """
    Decorator to inject the state manager into the context, using the username from the context.
    """

    @wraps(func)
    def wrapper(ctx: Context, *args: T.args, **kwargs: T.kwargs) -> R:
        if ctx.get_state("state") is None:
            username = ctx.get_state("username")
            if username is None:
                raise ValueError("Username is not set in the context")
            ctx.set_state("state", GameStateRepository.for_user(username))
        return func(ctx, *args, **kwargs)

    return wrapper
