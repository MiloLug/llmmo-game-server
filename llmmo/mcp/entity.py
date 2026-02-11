from typing import Annotated
from fastmcp import Context, FastMCP
from llmmo.mcp.common_types import EntityId, LocationId
from llmmo.auth import with_mcp_auth
from llmmo.state import with_state
from llmmo.state import Entity

mcp = FastMCP("Entity management")


@mcp.tool
@with_mcp_auth
@with_state
def create(
    ctx: Context,
    name: Annotated[str, "The name of the entity"],
    description: Annotated[
        str,
        "The short description of the entity. It should include its purpose and its use cases.",
    ],
    location_id: Annotated[
        LocationId, "The ID of the location where the entity is located."
    ],
) -> Entity:
    """Create a new entity in the game context. Returns created entity."""
    return ctx.get_state("state").entity.create(name, description, location_id)


@mcp.tool
@with_mcp_auth
@with_state
def edit(
    ctx: Context,
    entity_id: EntityId,
    description: Annotated[
        str,
        "The new description of the entity. It should include its purpose and its use cases.",
    ]
    | None = None,
    location_id: Annotated[
        LocationId, "The new ID of the location where the entity is located."
    ]
    | None = None,
) -> Entity:
    """Edit an existing entity in the game context. Returns the edited entity."""
    return ctx.get_state("state").entity.update(entity_id, description, location_id)


@mcp.tool
@with_mcp_auth
@with_state
def get(
    ctx: Context,
    entity_id: EntityId,
) -> Entity:
    """Get an existing entity in the game context. Returns the entity's details."""
    return ctx.get_state("state").entity.get(entity_id)


@mcp.tool
@with_mcp_auth
@with_state
def get_all(ctx: Context) -> list[Entity]:
    """Get all entities in the whole game context. Uses a lot of context. Not recommended."""
    return ctx.get_state("state").entity.get_all()


@mcp.tool
@with_mcp_auth
@with_state
def get_all_at_location(ctx: Context, location_id: LocationId) -> list[Entity]:
    """Get all entities at a specific location in the game context. Returns a list of entity details."""
    return ctx.get_state("state").entity.get_all_at_location(location_id)
