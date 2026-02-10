from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from pydantic import BaseModel

if TYPE_CHECKING:
    from llmmo.state.manager import GameStateManager


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
