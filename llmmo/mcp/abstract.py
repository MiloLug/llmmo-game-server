from typing import Annotated
from fastmcp import Context, FastMCP
from llmmo.mcp.common_types import AbstractId
from llmmo.state import Abstract, ObjectType
from llmmo.auth import with_mcp_auth
from llmmo.state import with_state
from uuid import UUID

mcp = FastMCP("Abstract management")


@mcp.tool
@with_mcp_auth
@with_state
def create(
    ctx: Context,
    name: Annotated[str, "The name of the abstract"],
    description: Annotated[
        str,
        "The short description of the abstract. It should include its purpose and its use cases.",
    ],
) -> Abstract:
    """Create a new abstract in the game context. Returns created abstract."""
    return ctx.get_state("state").abstract.create(name, description)


@mcp.tool
@with_mcp_auth
@with_state
def edit(
    ctx: Context,
    abstract_id: AbstractId,
    description: Annotated[
        str,
        "The new description of the abstract. It should include its purpose and its use cases.",
    ],
) -> Abstract:
    """Edit an existing abstract in the game context. Returns the edited abstract."""
    return ctx.get_state("state").abstract.edit(abstract_id, description)


@mcp.tool
@with_mcp_auth
@with_state
def get(
    ctx: Context,
    abstract_id: AbstractId,
) -> Abstract:
    """Get an existing abstract in the game context. Returns the abstract's details."""
    return ctx.get_state("state").abstract.get(abstract_id)


@mcp.tool
@with_mcp_auth
@with_state
def get_all(ctx: Context) -> list[Abstract]:
    """Get all abstracts in the whole game context. Uses a lot of context. Not recommended."""
    return ctx.get_state("state").abstract.get_all()


@mcp.tool
@with_mcp_auth
@with_state
def add_context(
    ctx: Context,
    abstract_id: AbstractId,
    object_type: Annotated[ObjectType, "The type of the object to add to the context"],
    object_id: Annotated[
        UUID, "The ID of the object of given type to add to the context"
    ],
) -> Abstract:
    """Add a context to an existing abstract in the game context. Returns the abstract with the new context."""
    return ctx.get_state("state").abstract.add_context(
        abstract_id, object_type, object_id
    )


@mcp.tool
@with_mcp_auth
@with_state
def remove_context(
    ctx: Context,
    abstract_id: AbstractId,
    object_id: Annotated[UUID, "The ID of the object to remove from the context"],
) -> Abstract:
    """Remove a context from an existing abstract in the game context. Returns the abstract with the removed context."""
    return ctx.get_state("state").abstract.remove_context(abstract_id, object_id)
