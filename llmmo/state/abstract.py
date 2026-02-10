from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from pydantic import BaseModel

if TYPE_CHECKING:
    from llmmo.state.manager import GameStateManager


class Abstract(BaseModel):
    """It can be anything that is important to remember as is AND is abstract. Event, topic, memory, etc."""

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
