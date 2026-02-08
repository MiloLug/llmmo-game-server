from functools import cache, wraps
from typing import Callable, Concatenate, Self
from uuid import UUID, uuid4
from fastmcp import Context
from pydantic import BaseModel, Field
from pathlib import Path

from llmmo.config.settings import config
from llmmo.utils import json_dumps, json_loads


# TODO: Later, use sql or mongodb to store the game state.


class Item(BaseModel):
    """An item in the game. It can be a weapon, a tool, a resource, etc."""

    id: UUID
    name: str
    description: str


class ItemManager:
    def __init__(self, repository: GameStateManager):
        self.repository = repository

    def get(self, item_id: UUID) -> Item:
        if item_id not in self.repository.state.items:
            raise ValueError(f"Item {item_id} not found")
        return self.repository.state.items[item_id]

    def get_all(self) -> list[Item]:
        return list(self.repository.state.items.values())

    def create(self, name: str, description: str) -> Item:
        item = Item(id=uuid4(), name=name, description=description)
        self.repository.state.items[item.id] = item
        self.repository.save()
        return item

    def edit(self, item_id: UUID, description: str | None = None) -> Item:
        item = self.get(item_id)
        if description is not None:
            item.description = description
        self.repository.save()
        return item


class Player(BaseModel):
    """A player in the game. It can be a human player, a computer player, etc."""

    id: UUID
    name: str
    inventory: dict[UUID, int] = Field(default_factory=dict)
    location_id: UUID


class PlayerManager:
    def __init__(self, state: GameStateManager):
        self.repository = state

    def get(self, player_id: UUID) -> Player:
        if player_id not in self.repository.state.players:
            raise ValueError(f"Player {player_id} not found")
        return self.repository.state.players[player_id]

    def get_all(self) -> list[Player]:
        return list(self.repository.state.players.values())

    def create(
        self, name: str, location_id: UUID, set_as_current: bool = True
    ) -> Player:
        player = Player(id=uuid4(), name=name, location_id=location_id)
        self.repository.state.players[player.id] = player
        if set_as_current:
            self.repository.state.current_player_id = player.id
        self.repository.save()
        return player

    def set_current(self, player_id: UUID) -> Player:
        player = self.get(player_id)
        self.repository.state.current_player_id = player.id
        self.repository.save()
        return player

    def get_current(self) -> Player:
        if self.repository.state.current_player_id is None:
            raise ValueError("No current player")
        return self.get(self.repository.state.current_player_id)

    def get_inventory(self, player_id: UUID) -> list[Item]:
        return [
            self.repository.item.get(item_id)
            for item_id in self.get(player_id).inventory
        ]

    def add_item(
        self, player_id: UUID, item_id: UUID, quantity: int = 1
    ) -> dict[UUID, int]:
        if quantity <= 0:
            raise ValueError("Quantity must be positive")
        item = self.repository.item.get(item_id)
        player = self.get(player_id)
        player.inventory[item.id] = player.inventory.get(item.id, 0) + quantity
        self.repository.save()
        return player.inventory

    def remove_item(
        self, player_id: UUID, item_id: UUID, quantity: int = 1
    ) -> dict[UUID, int]:
        if quantity <= 0:
            raise ValueError("Quantity must be positive")
        item = self.repository.item.get(item_id)
        player = self.get(player_id)
        current_quantity = player.inventory.get(item.id, 0)
        if current_quantity < quantity:
            raise ValueError(
                f"Player {player_id} does not have {quantity} {item.name} in inventory"
            )
        new_quantity = current_quantity - quantity
        if new_quantity == 0:
            del player.inventory[item.id]
        else:
            player.inventory[item.id] = new_quantity
        self.repository.save()
        return player.inventory

    def remove_item_full(self, player_id: UUID, item_id: UUID) -> dict[UUID, int]:
        player = self.get(player_id)
        item = self.repository.item.get(item_id)
        if item.id not in player.inventory:
            raise ValueError(
                f"Player {player_id} does not have {item.name} in inventory"
            )
        del player.inventory[item.id]
        self.repository.save()
        return player.inventory

    def move_to(self, player_id: UUID, location_id: UUID) -> Player:
        player = self.get(player_id)
        player.location_id = self.repository.location.get(
            location_id
        ).id  # to be sure it exists
        self.repository.save()
        return player


class Location(BaseModel):
    """A location in the game. It can be a room, a building, a field, etc."""

    id: UUID
    name: str
    description: str


class LocationManager:
    def __init__(self, repository: GameStateManager):
        self.repository = repository

    def get(self, location_id: UUID) -> Location:
        if location_id not in self.repository.state.locations:
            raise ValueError(f"Location {location_id} not found")
        return self.repository.state.locations[location_id]

    def get_all(self) -> list[Location]:
        return list(self.repository.state.locations.values())

    def create(self, name: str, description: str) -> Location:
        location = Location(id=uuid4(), name=name, description=description)
        self.repository.state.locations[location.id] = location
        self.repository.save()
        return location

    def get_current(self) -> Location:
        return self.get(self.repository.player.get_current().location_id)

    def edit(self, location_id: UUID, description: str | None = None) -> Location:
        location = self.get(location_id)
        if description is not None:
            location.description = description
        self.repository.save()
        return location


class Abstract(BaseModel):
    """It can be anything that is important to remember as is. Event, topic etc."""

    id: UUID
    name: str
    description: str


class AbstractManager:
    def __init__(self, repository: GameStateManager):
        self.repository = repository

    def get(self, abstract_id: UUID) -> Abstract:
        if abstract_id not in self.repository.state.abstracts:
            raise ValueError(f"Abstract {abstract_id} not found")
        return self.repository.state.abstracts[abstract_id]

    def get_all(self) -> list[Abstract]:
        return list(self.repository.state.abstracts.values())

    def create(self, name: str, description: str) -> Abstract:
        abstract = Abstract(id=uuid4(), name=name, description=description)
        self.repository.state.abstracts[abstract.id] = abstract
        self.repository.save()
        return abstract

    def edit(self, abstract_id: UUID, description: str | None = None) -> Abstract:
        abstract = self.get(abstract_id)
        if description is not None:
            abstract.description = description
        self.repository.save()
        return abstract


class Entity(BaseModel):
    """An entity in the game. It can be a chest, a tree, a monster, etc."""

    id: UUID
    name: str
    description: str
    location_id: UUID | None = None


class EntityManager:
    def __init__(self, repository: GameStateManager):
        self.repository = repository

    def get(self, entity_id: UUID) -> Entity:
        if entity_id not in self.repository.state.entities:
            raise ValueError(f"Entity {entity_id} not found")
        return self.repository.state.entities[entity_id]

    def get_all(self) -> list[Entity]:
        return list(self.repository.state.entities.values())

    def create(self, name: str, description: str, location_id: UUID) -> Entity:
        entity = Entity(
            id=uuid4(), name=name, description=description, location_id=location_id
        )
        self.repository.state.entities[entity.id] = entity
        self.repository.save()
        return entity

    def edit(
        self,
        entity_id: UUID,
        description: str | None = None,
        location_id: UUID | None = None,
    ) -> Entity:
        entity = self.get(entity_id)
        if description is not None:
            entity.description = description
        if location_id is not None:
            entity.location_id = location_id
        self.repository.save()
        return entity

    def get_all_at_location(self, location_id: UUID) -> list[Entity]:
        return [
            entity for entity in self.get_all() if entity.location_id == location_id
        ]


class GameState(BaseModel):
    setting: str = ""
    save_summary: str = ""
    locations: dict[UUID, Location] = Field(default_factory=dict)
    players: dict[UUID, Player] = Field(default_factory=dict)
    current_player_id: UUID | None = None
    items: dict[UUID, Item] = Field(default_factory=dict)
    abstracts: dict[UUID, Abstract] = Field(default_factory=dict)
    entities: dict[UUID, Entity] = Field(default_factory=dict)


class GameStateManager:
    def __init__(self, path: Path):
        self.state = GameState()
        self.path = path

        self.location = LocationManager(self)
        self.player = PlayerManager(self)
        self.item = ItemManager(self)
        self.abstract = AbstractManager(self)
        self.entity = EntityManager(self)

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
            ctx.set_state("state", GameStateManager.for_user(username))
        return func(ctx, *args, **kwargs)

    return wrapper
