from typing import Annotated
from uuid import UUID


type ItemId = Annotated[UUID, "The ID of Item instance"]
type LocationId = Annotated[UUID, "The ID of Location instance"]
type AbstractId = Annotated[UUID, "The ID of Abstract instance"]
type EntityId = Annotated[UUID, "The ID of Entity instance"]
type PlayerId = Annotated[UUID, "The ID of Player instance"]
