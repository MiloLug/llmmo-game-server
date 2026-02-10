from __future__ import annotations

from enum import StrEnum
from uuid import UUID, uuid4

from pydantic import BaseModel, Field

from llmmo.state.base_manager import BaseManager, BaseObject


class ObjectType(StrEnum):
    ITEM = "ITEM"
    LOCATION = "LOCATION"
    ENTITY = "ENTITY"
    ABSTRACT = "ABSTRACT"


class ContextRelation(BaseModel):
    object_type: ObjectType
    id: UUID


class Abstract(BaseObject):
    """It can be anything that is important to remember as is AND is abstract. Event, topic, memory, etc."""

    name: str
    description: str
    context: dict[UUID, ObjectType] = Field(default_factory=dict)


class AbstractManager(BaseManager[Abstract]):
    def get(self, id: UUID) -> Abstract:
        if id not in self.repository.state.abstracts:
            raise ValueError(f"Abstract {id} not found")
        return self.repository.state.abstracts[id]

    def get_all(self) -> list[Abstract]:
        return list(self.repository.state.abstracts.values())

    def create(self, name: str, description: str) -> Abstract:
        abstract = Abstract(id=uuid4(), name=name, description=description)
        self.repository.state.abstracts[abstract.id] = abstract
        self.repository.save()
        return abstract

    def update(self, abstract_id: UUID, description: str | None = None) -> Abstract:
        abstract = self.get(abstract_id)
        if description is not None:
            abstract.description = description
        self.repository.save()
        return abstract

    def _get_relation_object(
        self, object_type: ObjectType, object_id: UUID
    ) -> BaseObject:
        match object_type:
            case ObjectType.ITEM:
                return self.repository.item.get(object_id)
            case ObjectType.LOCATION:
                return self.repository.location.get(object_id)
            case ObjectType.ENTITY:
                return self.repository.entity.get(object_id)
            case ObjectType.ABSTRACT:
                return self.repository.abstract.get(object_id)

    def add_context(
        self, id: UUID, object_type: ObjectType, object_id: UUID
    ) -> Abstract:
        abstract = self.get(id)
        obj = self._get_relation_object(object_type, object_id)
        abstract.context[obj.id] = object_type
        self.repository.save()
        return abstract

    def remove_context(self, id: UUID, object_id: UUID) -> Abstract:
        abstract = self.get(id)
        abstract.context.pop(object_id)
        self.repository.save()
        return abstract
