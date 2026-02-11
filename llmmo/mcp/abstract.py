from typing import Annotated
from fastmcp import Context, FastMCP
from pydantic import BaseModel
from llmmo.mcp.common_types import AbstractId
from llmmo.state import Abstract, ObjectType
from llmmo.state.repository import GameStateRepository
from llmmo.auth import with_mcp_auth
from llmmo.state import with_state
from uuid import UUID


class ContextEntry(BaseModel):
    id: UUID
    name: str
    object_type: ObjectType


class AbstractWithContext(BaseModel):
    id: UUID
    name: str
    description: str
    context: list[ContextEntry]

    @classmethod
    def from_abstract(
        cls, repo: GameStateRepository, abstract: Abstract
    ) -> "AbstractWithContext":
        entries = []
        for obj_id, obj_type in abstract.context.items():
            obj = repo.get_object(obj_type, obj_id)
            entries.append(ContextEntry(id=obj.id, name=obj.name, object_type=obj_type))
        return cls(
            id=abstract.id,
            name=abstract.name,
            description=abstract.description,
            context=entries,
        )


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
) -> AbstractWithContext:
    """Create a new abstract in the game context. Returns created abstract."""
    repo: GameStateRepository = ctx.get_state("state")
    return AbstractWithContext.from_abstract(
        repo, repo.abstract.create(name, description)
    )


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
) -> AbstractWithContext:
    """Edit an existing abstract in the game context. Returns the edited abstract."""
    repo: GameStateRepository = ctx.get_state("state")
    return AbstractWithContext.from_abstract(
        repo, repo.abstract.update(abstract_id, description)
    )


@mcp.tool
@with_mcp_auth
@with_state
def get(
    ctx: Context,
    abstract_id: AbstractId,
) -> AbstractWithContext:
    """Get an existing abstract in the game context. Returns the abstract's details."""
    repo: GameStateRepository = ctx.get_state("state")
    return AbstractWithContext.from_abstract(repo, repo.abstract.get(abstract_id))


@mcp.tool
@with_mcp_auth
@with_state
def get_all(ctx: Context) -> list[AbstractWithContext]:
    """Get all abstracts in the whole game context. Uses a lot of context. Not recommended."""
    repo: GameStateRepository = ctx.get_state("state")
    return [
        AbstractWithContext.from_abstract(repo, abstract)
        for abstract in repo.abstract.get_all()
    ]


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
) -> AbstractWithContext:
    """
    Add an object of given type and ID to the context of an existing abstract in the game context.
    This allows to link objects for easier reasoning and memory.
    Returns the abstract with the new context.
    """
    repo: GameStateRepository = ctx.get_state("state")
    return AbstractWithContext.from_abstract(
        repo, repo.abstract.add_context(abstract_id, object_type, object_id)
    )


@mcp.tool
@with_mcp_auth
@with_state
def remove_context(
    ctx: Context,
    abstract_id: AbstractId,
    object_id: Annotated[UUID, "The ID of the object to remove from the context"],
) -> AbstractWithContext:
    """Remove a context from an existing abstract in the game context. Returns the abstract with the removed context."""
    repo: GameStateRepository = ctx.get_state("state")
    return AbstractWithContext.from_abstract(
        repo, repo.abstract.remove_context(abstract_id, object_id)
    )
