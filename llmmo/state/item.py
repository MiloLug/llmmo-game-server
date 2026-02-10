from __future__ import annotations

from uuid import UUID, uuid4

from llmmo.state.base_manager import BaseManager, BaseObject


class Item(BaseObject):
    """An item in the game. It can be a weapon, a tool, a resource, etc."""

    name: str
    description: str


class ItemManager(BaseManager[Item]):
    def get(self, id: UUID) -> Item:
        if id not in self.repository.state.items:
            raise ValueError(f"Item {id} not found")
        return self.repository.state.items[id]

    def get_all(self) -> list[Item]:
        return list(self.repository.state.items.values())

    def create(self, name: str, description: str) -> Item:
        item = Item(id=uuid4(), name=name, description=description)
        self.repository.state.items[item.id] = item
        self.repository.save()
        return item

    def update(self, id: UUID, description: str | None = None) -> Item:
        item = self.get(id)
        if description is not None:
            item.description = description
        self.repository.save()
        return item
