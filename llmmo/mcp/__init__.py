from typing import Annotated
from fastmcp import FastMCP, Context
from pydantic import BaseModel
from llmmo.state import Location, Player
from llmmo.mcp.item import mcp as item_mcp
from llmmo.mcp.location import mcp as location_mcp
from llmmo.mcp.player import mcp as player_mcp
from llmmo.mcp.entity import mcp as entity_mcp
from llmmo.mcp.abstract import mcp as abstract_mcp
from llmmo.auth import with_mcp_auth
from llmmo.state import with_state


mcp = FastMCP("llmmo game management")
mcp.mount(prefix="Item", server=item_mcp)
mcp.mount(prefix="Location", server=location_mcp)
mcp.mount(prefix="Player", server=player_mcp)
mcp.mount(prefix="Entity", server=entity_mcp)
mcp.mount(prefix="Abstract", server=abstract_mcp)

mcp_asgi = mcp.http_app(path="/")


class ShortWorldStateResponse(BaseModel):
    setting: str = ""
    save_summary: str = ""
    current_player: Player
    current_location: Location


@mcp.tool
@with_mcp_auth
@with_state
def resume_game(ctx: Context) -> ShortWorldStateResponse:
    """Get the game setting and previous save summary. Should be called when the user starts a new chat."""
    state = ctx.get_state("state")
    return ShortWorldStateResponse(
        setting=state.state.setting,
        save_summary=state.state.save_summary,
        current_player=state.player.get_current(),
        current_location=state.location.get_current(),
    )


@mcp.tool
@with_mcp_auth
@with_state
def save_game(
    ctx: Context,
    save_summary: Annotated[
        str,
        "The summary of the game. It should be a short description of the game state.",
    ],
) -> str:
    """Save the game with the given save summary before exiting the chat or just by user request."""
    ctx.get_state("state").save_game(save_summary)
    return "Game saved"


@mcp.tool
@with_mcp_auth
@with_state
def start_game(
    ctx: Context,
    setting: Annotated[
        str,
        "The overall setting of the game. Should be a medium-long text describing the game world and its rules.",
    ],
    player_name: Annotated[
        str, "The name of the player. It should be a 1-2 words name."
    ],
    location_name: Annotated[str, "The name of the location."],
    location_description: Annotated[
        str,
        "The description of the location. It should include local setting, context and very brief history of the location.",
    ],
) -> ShortWorldStateResponse:
    """Start a new game with the given setting"""
    state = ctx.get_state("state")
    state.start_game(setting, player_name, location_name, location_description)
    return ShortWorldStateResponse(
        setting=state.state.setting,
        save_summary=state.state.save_summary,
        current_player=state.player.get_current(),
        current_location=state.location.get_current(),
    )
