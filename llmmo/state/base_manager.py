from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any
from uuid import UUID

from pydantic import BaseModel

if TYPE_CHECKING:
    from llmmo.state.repository import GameStateRepository


class BaseObject(BaseModel):
    id: UUID


class BaseManager[T: BaseObject](ABC):
    def __init__(self, repository: GameStateRepository):
        self.repository = repository

    @abstractmethod
    def get(self, id: UUID) -> T: ...

    @abstractmethod
    def get_all(self) -> list[T]: ...

    @abstractmethod
    def create(self, *args: Any, **kwargs: Any) -> T: ...

    @abstractmethod
    def update(self, id: UUID, *args: Any, **kwargs: Any) -> T: ...
