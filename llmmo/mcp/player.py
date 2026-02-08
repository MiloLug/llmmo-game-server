from fastmcp import Context, FastMCP
from llmmo.auth import with_mcp_auth
from llmmo.state import with_state
from llmmo.state import Player
from llmmo.mcp.common_types import LocationId, PlayerId, ItemId
from llmmo.state import Item
from typing import Annotated
from uuid import UUID

mcp = FastMCP("Player management")


@mcp.tool
@with_mcp_auth
@with_state
def create(
    ctx: Context,
    name: Annotated[str, "The name of the player"],
    location_id: Annotated[
        LocationId, "The ID of the location where the player is spawned."
    ],
    set_as_current: Annotated[
        bool, "Whether to set the player as current. Defaults to True."
    ] = True,
) -> Player:
    """
    Create a new player in the game context. Later this player can be used to interact with the game.
    This player will be spawned at the given location. You don't need to call get_current after this. Returns created player.
    """
    return ctx.get_state("state").player.create(name, location_id, set_as_current)


@mcp.tool
@with_mcp_auth
@with_state
def get(
    ctx: Context,
    player_id: PlayerId,
) -> Player:
    """Get a player by their ID. Returns the player's details."""
    return ctx.get_state("state").player.get(player_id)


@mcp.tool
@with_mcp_auth
@with_state
def get_all(ctx: Context) -> list[Player]:
    """Get all players in the whole game context. Returns a list of player details."""
    return ctx.get_state("state").player.get_all()


@mcp.tool
@with_mcp_auth
@with_state
def set_current(
    ctx: Context,
    player_id: PlayerId,
) -> Player:
    """Set the current player by their ID. This player will be used to interact with the game. Returns the player's details."""
    return ctx.get_state("state").player.set_current(player_id)


@mcp.tool
@with_mcp_auth
@with_state
def get_current(ctx: Context) -> Player:
    """Get the current player's details."""
    return ctx.get_state("state").player.get_current()


@mcp.tool
@with_mcp_auth
@with_state
def get_inventory(
    ctx: Context,
    player_id: PlayerId,
) -> list[Item]:
    """Get the inventory of a player by their ID. Returns a list of item details."""
    return ctx.get_state("state").player.get_inventory(player_id)


@mcp.tool
@with_mcp_auth
@with_state
def add_item(
    ctx: Context,
    player_id: PlayerId,
    item_id: ItemId,
    quantity: Annotated[int, "The quantity of the item to add. Defaults to 1."] = 1,
) -> dict[UUID, int]:
    """Add an item to a player's inventory by their ID. Returns the short inventory summary."""
    return ctx.get_state("state").player.add_item(player_id, item_id, quantity)


@mcp.tool
@with_mcp_auth
@with_state
def remove_item(
    ctx: Context,
    player_id: PlayerId,
    item_id: ItemId,
    quantity: Annotated[int, "The quantity of the item to remove. Defaults to 1."] = 1,
) -> dict[UUID, int]:
    """Remove a quantity of an item from a player's inventory by their ID. Returns the short inventory summary."""
    return ctx.get_state("state").player.remove_item(player_id, item_id, quantity)


@mcp.tool
@with_mcp_auth
@with_state
def remove_item_full(
    ctx: Context,
    player_id: PlayerId,
    item_id: ItemId,
) -> dict[UUID, int]:
    """Remove an item completely from a player's inventory by their ID. Returns the short inventory summary."""
    return ctx.get_state("state").player.remove_item_full(player_id, item_id)


@mcp.tool
@with_mcp_auth
@with_state
def move_to(
    ctx: Context,
    player_id: PlayerId,
    location_id: LocationId,
) -> Player:
    """Move a player to a different location by their ID. Returns the player's details."""
    return ctx.get_state("state").player.move_to(player_id, location_id)
