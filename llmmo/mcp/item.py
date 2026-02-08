from typing import Annotated
from fastmcp import Context, FastMCP
from llmmo.mcp.common_types import ItemId
from llmmo.auth import with_mcp_auth
from llmmo.state import with_state
from llmmo.state import Item

mcp = FastMCP("Item management")


@mcp.tool
@with_mcp_auth
@with_state
def create(
    ctx: Context,
    name: Annotated[str, "The name of the item"],
    description: Annotated[
        str,
        "The short description of the item. It should include its purpose and its use cases.",
    ],
) -> Item:
    """Create a new item in the game context. Returns created item."""
    return ctx.get_state("state").item.create(name, description)


@mcp.tool
@with_mcp_auth
@with_state
def edit(
    ctx: Context,
    item_id: ItemId,
    description: Annotated[
        str,
        "The new description of the item. It should include its purpose and its use cases.",
    ]
    | None = None,
) -> Item:
    """Edit an existing item in the game context. Returns the edited item."""
    return ctx.get_state("state").item.edit(item_id, description)


@mcp.tool
@with_mcp_auth
@with_state
def get(
    ctx: Context,
    item_id: ItemId,
) -> Item:
    """Get an existing item in the game context. Returns the item's details."""
    return ctx.get_state("state").item.get(item_id)


@mcp.tool
@with_mcp_auth
@with_state
def get_all(ctx: Context) -> list[Item]:
    """Get all items in the whole game context. Uses a lot of context. Not recommended."""
    return ctx.get_state("state").item.get_all()
