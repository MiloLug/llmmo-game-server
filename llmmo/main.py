from llmmo.mcp import mcp_asgi
from llmmo.routes import router
from llmmo.auth import APIKeyAuthASGI
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from llmmo.config.settings import config


app = FastAPI(
    lifespan=mcp_asgi.lifespan,
    title="LLMMO Game Server",
    description="A game server for the LLMMO game",
    version="0.1.0",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=config().cors.origins,
    allow_credentials=config().cors.credentials,
    allow_methods=config().cors.methods,
    allow_headers=config().cors.headers,
)
app.include_router(router)
app.mount("/mcp", APIKeyAuthASGI(mcp_asgi))
