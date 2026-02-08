from typing import Annotated
from uuid import UUID
from fastmcp import Context, FastMCP
from llmmo.auth import with_mcp_auth
from llmmo.state import with_state
from llmmo.mcp.common_types import LocationId
from llmmo.state import Location

mcp = FastMCP("Location management")


@mcp.tool
@with_mcp_auth
@with_state
def create(
    ctx: Context,
    name: Annotated[str, "The name of the location"],
    description: Annotated[
        str,
        "The short description of the location. It should include its purpose and its use cases.",
    ],
) -> Location:
    """Create a new location in the game context. Returns the location's details."""
    return ctx.get_state("state").location.create(name, description)


@mcp.tool
@with_mcp_auth
@with_state
def edit(
    ctx: Context,
    location_id: LocationId,
    description: Annotated[
        str,
        "The new description of the location. It should include its purpose and its use cases.",
    ]
    | None = None,
) -> Location:
    """Edit an existing location in the game context. Returns the edited location."""
    return ctx.get_state("state").location.edit(location_id, description)


@mcp.tool
@with_mcp_auth
@with_state
def get(
    ctx: Context,
    location_id: LocationId,
) -> Location:
    """Get an existing location in the game context. Returns the location's details."""
    return ctx.get_state("state").location.get(location_id)


@mcp.tool
@with_mcp_auth
@with_state
def get_all(ctx: Context) -> list[Location]:
    """Get all locations in the whole game context. Returns a list of location details."""
    return ctx.get_state("state").location.get_all()


@mcp.tool
@with_mcp_auth
@with_state
def get_current(ctx: Context) -> Location:
    """Get the current location's details. Returns the location where the current player is."""
    return ctx.get_state("state").location.get_current()


@mcp.tool
@with_mcp_auth
@with_state
def get_all_short(ctx: Context) -> list[tuple[UUID, str]]:
    """Get all locations in the whole game context. Returns a list of ONLY ID and NAME. Useful for search without spending much context."""
    return [
        (location.id, location.name)
        for location in ctx.get_state("state").location.get_all()
    ]
