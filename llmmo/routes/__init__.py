from pathlib import Path

from fastapi import APIRouter, Form, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

from llmmo.auth import auth_manager

router = APIRouter()

TEMPLATES_DIR = Path(__file__).resolve().parent.parent / "templates"


class CredentialsRequest(BaseModel):
    username: str
    password: str


class APIKeyResponse(BaseModel):
    api_key: str


# ── JSON API ─────────────────────────────────────────────


@router.post("/auth/api-keys")
async def create_api_key_json(req: CredentialsRequest) -> APIKeyResponse:
    """Authenticate with username/password and receive a new API key."""
    try:
        username_hash = auth_manager().authenticate(req.username, req.password)
        api_key = auth_manager().create_api_key(username_hash)
        return APIKeyResponse(api_key=api_key)
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))


# ── HTML pages ───────────────────────────────────────────


def _render(
    title: str,
    action: str,
    btn_class: str,
    alt_link: str,
    message: str = "",
    message_ok: bool = True,
    api_key: str = "",
) -> HTMLResponse:
    from jinja2 import Template

    template = Template(TEMPLATES_DIR.joinpath("auth.html").read_text())
    html = template.render(
        title=title,
        action=action,
        btn_class=btn_class,
        alt_link=alt_link,
        message=message,
        message_ok=message_ok,
        api_key=api_key,
    )
    return HTMLResponse(html)


@router.get("/register", response_class=HTMLResponse)
async def register_page():
    return _render(
        title="Register",
        action="Register",
        btn_class="register",
        alt_link='<a href="/login">Already have an account? Login</a>',
    )


@router.post("/register", response_class=HTMLResponse)
async def register_submit(username: str = Form(), password: str = Form()):
    msg, ok, key = "", True, ""
    try:
        username_hash = auth_manager().register(username, password)
        key = auth_manager().create_api_key(username_hash)
        msg = "Registered successfully! Here is your API key:"
    except ValueError as e:
        msg, ok = str(e), False
    return _render(
        title="Register",
        action="Register",
        btn_class="register",
        alt_link='<a href="/login">Already have an account? Login</a>',
        message=msg,
        message_ok=ok,
        api_key=key,
    )


@router.get("/login", response_class=HTMLResponse)
async def login_page():
    return _render(
        title="Login",
        action="Login",
        btn_class="login",
        alt_link='<a href="/register">No account? Register</a>',
    )


@router.post("/login", response_class=HTMLResponse)
async def login_submit(username: str = Form(), password: str = Form()):
    msg, ok, key = "", True, ""
    try:
        username_hash = auth_manager().authenticate(username, password)
        key = auth_manager().create_api_key(username_hash)
        msg = "Login successful! Here is your API key:"
    except ValueError as e:
        msg, ok = str(e), False
    return _render(
        title="Login",
        action="Login",
        btn_class="login",
        alt_link='<a href="/register">No account? Register</a>',
        message=msg,
        message_ok=ok,
        api_key=key,
    )
