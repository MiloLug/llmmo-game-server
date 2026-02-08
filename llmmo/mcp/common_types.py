from typing import Annotated
from uuid import UUID
from fastmcp.tools.tool_transform import ArgTransform

ITEM_ARG = ArgTransform(description="The ID of Item instance")
LOCATION_ARG = ArgTransform(description="The ID of Location instance")
ABSTRACT_ARG = ArgTransform(description="The ID of Abstract instance")
ENTITY_ARG = ArgTransform(description="The ID of Entity instance")
PLAYER_ARG = ArgTransform(description="The ID of Player instance")


type ItemId = Annotated[UUID, "The ID of Item instance"]
type LocationId = Annotated[UUID, "The ID of Location instance"]
type AbstractId = Annotated[UUID, "The ID of Abstract instance"]
type EntityId = Annotated[UUID, "The ID of Entity instance"]
type PlayerId = Annotated[UUID, "The ID of Player instance"]
