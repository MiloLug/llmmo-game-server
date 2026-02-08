# LLMMO Game Server

MCP server for LLM-driven text game state management. Exposes tools for managing players, locations, items, entities, and abstract concepts via the MCP protocol.

Built with FastAPI, FastMCP, Python 3.14.

## Setup

### Docker (recommended)

```bash
cp .env.example .env  # adjust if needed
docker compose up --build app
```

### Local

```bash
uv sync
uvicorn llmmo.main:app --reload --host 0.0.0.0 --port 8111
```

## Configuration

Environment variables (`.env`):

| Variable | Default | Description |
|---|---|---|
| `BACKEND__RUN__HOST` | `localhost` | Server host |
| `BACKEND__RUN__PORT` | `8111` | Server port |
| `BACKEND__DB__BASE_PATH` | `.state` | Game state storage directory |
| `BACKEND__CORS__ORIGINS` | `["http://localhost:8111"]` | Allowed CORS origins |
| `BACKEND__CORS__CREDENTIALS` | `true` | Allow credentials |
| `BACKEND__CORS__METHODS` | `["*"]` | Allowed HTTP methods |
| `BACKEND__CORS__HEADERS` | `["*"]` | Allowed headers |

## Authentication

1. Register at `GET /register` or `POST /register`
2. Get an API key via `POST /auth/api-keys` (JSON: `{"username": "...", "password": "..."}`)
3. Use the key as a Bearer token for MCP endpoints: `Authorization: Bearer <api_key>`

Each user gets isolated game state stored in `.state/<username_hash>/`.

## MCP Endpoint

MCP server is mounted at `/mcp`. Connect your MCP client to `http://localhost:8111/mcp`.

## Data Model

- **Player** — name, inventory (`item_id -> quantity`), current location
- **Location** — name, description
- **Item** — name, description (global, referenced by players)
- **Entity** — name, description, optional location (NPCs, objects, monsters)
- **Abstract** — name, description (events, topics, lore — not tied to locations)

All IDs are UUIDs. State is persisted as JSON files per user.

## Development

```bash
uv sync --all-groups  # install dev deps
```

Before commit: `ruff` (lint/format), `mypy` (type check).
