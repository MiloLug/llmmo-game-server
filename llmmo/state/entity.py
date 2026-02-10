from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from pydantic import BaseModel

if TYPE_CHECKING:
    from llmmo.state.manager import GameStateManager


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
