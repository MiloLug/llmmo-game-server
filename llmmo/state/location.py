from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from pydantic import BaseModel

if TYPE_CHECKING:
    from llmmo.state.manager import GameStateManager


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
