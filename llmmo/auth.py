import contextvars
from functools import cache, wraps
import hashlib
import secrets
from pathlib import Path
from typing import Callable, Concatenate

from fastmcp import Context


current_username: contextvars.ContextVar[str | None] = contextvars.ContextVar(
    "current_username", default=None
)


class AuthManager:
    def __init__(self, base_path: Path):
        self.base_path = base_path
        self.api_keys_path = base_path / "api_keys"
        self.api_keys_path.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def hash_text(text: str) -> str:
        return hashlib.sha256(text.encode()).hexdigest()

    def register(self, username: str, password: str) -> str:
        safe_username = self.hash_text(username)
        safe_password = self.hash_text(password)
        user_file = self.base_path / safe_username
        if user_file.exists():
            raise ValueError("User already exists")

        user_file.touch()
        user_file.write_text(safe_password)
        return safe_username

    def authenticate(self, username: str, password: str) -> str:
        safe_username = self.hash_text(username)
        safe_password = self.hash_text(password)
        user_file = self.base_path / safe_username
        if user_file.exists() and user_file.read_text() == safe_password:
            return safe_username
        raise ValueError("Invalid username or password")

    def create_api_key(self, username_hash: str) -> str:
        """Create a new API key for the given user. Returns the raw key (shown only once)."""
        raw_key = secrets.token_urlsafe(32)
        key_hash = self.hash_text(raw_key)
        key_file = self.api_keys_path / key_hash
        key_file.write_text(username_hash)
        return raw_key

    def validate_api_key(self, api_key: str) -> str:
        """Validate an API key and return the username hash. Raises ValueError if invalid."""
        key_hash = self.hash_text(api_key)
        key_file = self.api_keys_path / key_hash
        if not key_file.exists():
            raise ValueError("Invalid API key")
        return key_file.read_text()


@cache
def auth_manager(base_path: Path = Path(".state/auth/")) -> AuthManager:
    base_path.mkdir(parents=True, exist_ok=True)
    return AuthManager(base_path)


def with_mcp_auth[**T, R](
    func: Callable[Concatenate[Context, T], R],
) -> Callable[Concatenate[Context, T], R]:
    """Decorator that injects the authenticated username (from API key) into the MCP context."""

    @wraps(func)
    def wrapper(ctx: Context, *args: T.args, **kwargs: T.kwargs) -> R:
        username = current_username.get()
        if username is None:
            raise ValueError("Not authenticated. Provide a valid API key.")
        ctx.set_state("username", username)
        return func(ctx, *args, **kwargs)

    return wrapper


class APIKeyAuthASGI:
    """ASGI middleware that validates Bearer API keys on incoming requests."""

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] in ("http", "websocket"):
            headers = dict(scope.get("headers", []))
            auth_header = headers.get(b"authorization", b"").decode()

            if auth_header.startswith("Bearer "):
                api_key = auth_header[7:]
                try:
                    username = auth_manager().validate_api_key(api_key)
                    token = current_username.set(username)
                    try:
                        await self.app(scope, receive, send)
                    finally:
                        current_username.reset(token)
                    return
                except ValueError:
                    pass

            if scope["type"] == "http":
                await self._send_401(send)
            return

        await self.app(scope, receive, send)

    @staticmethod
    async def _send_401(send):
        await send(
            {
                "type": "http.response.start",
                "status": 401,
                "headers": [[b"content-type", b"application/json"]],
            }
        )
        await send(
            {
                "type": "http.response.body",
                "body": b'{"error":"Invalid or missing API key"}',
            }
        )
