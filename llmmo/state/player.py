from __future__ import annotations

from uuid import UUID, uuid4

from typing import TYPE_CHECKING
from pydantic import BaseModel, Field
from llmmo.state.base_manager import BaseManager

if TYPE_CHECKING:
    from llmmo.state.item import Item


class Player(BaseModel):
    """A player in the game. It can be a human player, a computer player, etc."""

    id: UUID
    name: str
    inventory: dict[UUID, int] = Field(default_factory=dict)
    location_id: UUID


class PlayerManager(BaseManager[Player]):
    def get(self, id: UUID) -> Player:
        if id not in self.repository.state.players:
            raise ValueError(f"Player {id} not found")
        return self.repository.state.players[id]

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

    def update(self, id: UUID, name: str | None = None) -> Player:
        player = self.get(id)
        if name is not None:
            player.name = name
        self.repository.save()
        return player

    def set_current(self, id: UUID) -> Player:
        player = self.get(id)
        self.repository.state.current_player_id = player.id
        self.repository.save()
        return player

    def get_current(self) -> Player:
        if self.repository.state.current_player_id is None:
            raise ValueError("No current player")
        return self.get(self.repository.state.current_player_id)

    def get_inventory(self, id: UUID) -> list[Item]:
        return [self.repository.item.get(item_id) for item_id in self.get(id).inventory]

    def add_item(self, id: UUID, item_id: UUID, quantity: int = 1) -> dict[UUID, int]:
        if quantity <= 0:
            raise ValueError("Quantity must be positive")
        item = self.repository.item.get(item_id)
        player = self.get(id)
        player.inventory[item.id] = player.inventory.get(item.id, 0) + quantity
        self.repository.save()
        return player.inventory

    def remove_item(
        self, id: UUID, item_id: UUID, quantity: int = 1
    ) -> dict[UUID, int]:
        if quantity <= 0:
            raise ValueError("Quantity must be positive")
        item = self.repository.item.get(item_id)
        player = self.get(id)
        current_quantity = player.inventory.get(item.id, 0)
        if current_quantity < quantity:
            raise ValueError(
                f"Player {id} does not have {quantity} {item.name} in inventory"
            )
        new_quantity = current_quantity - quantity
        if new_quantity == 0:
            del player.inventory[item.id]
        else:
            player.inventory[item.id] = new_quantity
        self.repository.save()
        return player.inventory

    def remove_item_full(self, id: UUID, item_id: UUID) -> dict[UUID, int]:
        player = self.get(id)
        item = self.repository.item.get(item_id)
        if item.id not in player.inventory:
            raise ValueError(f"Player {id} does not have {item.name} in inventory")
        del player.inventory[item.id]
        self.repository.save()
        return player.inventory

    def move_to(self, id: UUID, location_id: UUID) -> Player:
        player = self.get(id)
        player.location_id = self.repository.location.get(
            location_id
        ).id  # to be sure it exists
        self.repository.save()
        return player
