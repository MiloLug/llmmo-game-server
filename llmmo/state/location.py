from __future__ import annotations

from uuid import UUID, uuid4

from llmmo.state.base_manager import BaseManager, BaseObject


class Location(BaseObject):
    """A location in the game. It can be a room, a building, a field, etc."""

    description: str


class LocationManager(BaseManager[Location]):
    def get(self, id: UUID) -> Location:
        if id not in self.repository.state.locations:
            raise ValueError(f"Location {id} not found")
        return self.repository.state.locations[id]

    def get_all(self) -> list[Location]:
        return list(self.repository.state.locations.values())

    def create(self, name: str, description: str) -> Location:
        location = Location(id=uuid4(), name=name, description=description)
        self.repository.state.locations[location.id] = location
        self.repository.save()
        return location

    def get_current(self) -> Location:
        return self.get(self.repository.player.get_current().location_id)

    def update(self, id: UUID, description: str | None = None) -> Location:
        location = self.get(id)
        if description is not None:
            location.description = description
        self.repository.save()
        return location
