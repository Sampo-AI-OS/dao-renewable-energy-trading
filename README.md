# DAO Renewable Energy Trading

DAO Renewable Energy Trading is a curated public-edition node from the Sampo AI OS ecosystem. It provides an energy-market subsystem around DAO Hub: synthetic market snapshots, renewable trade creation, optimization hints, and optional telemetry pushbacks into the governance hub.

This repository should be read as a standalone node around DAO Hub, not as the hub itself. DAO Hub remains the orchestration center. This node demonstrates how energy trading and market analytics can be exposed as an operational subsystem within the broader ecosystem.

See `PUBLIC_EDITION_SCOPE.md` for what is included here and what was intentionally left out.

![Python](https://img.shields.io/badge/Python-3.11+-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-service-009688)
![Docker](https://img.shields.io/badge/Docker-ready-blue)

## Dashboard Preview

![DAO Renewable Energy Trading dashboard](media/Screenshot%202026-04-07%20165017.png)

The preview shows the renewable energy market view with spot pricing, wind and solar generation, carbon intensity, history, and optimization controls.

## What This Node Does

The public edition exposes four core capability groups:

1. Market simulation
   Generate synthetic renewable generation, demand, spot-price, and carbon-intensity snapshots.

2. Trade management
   Create and list renewable energy trades tied to authenticated users.

3. Routing optimization
   Return lightweight AI-style routing and pricing suggestions for energy volumes.

4. DAO Hub telemetry
   Optionally push selected market and trade metrics back into DAO Hub without blocking local flows.

## Capability Summary

- authenticated trading workflow
- seeded local admin for quick evaluation
- synthetic renewable market snapshots persisted to the database
- trade creation and listing endpoints
- route optimization endpoint for energy type and quantity scenarios
- optional non-blocking DAO Hub metric push integration
- Docker and local dev workflow suitable for portfolio review

## Architecture Overview

The public edition keeps the original modular backend structure while simplifying the runtime defaults.

- `main.py` exposes the API surface and startup seeding
- `database.py` manages the SQLAlchemy engine and sessions
- `models.py` defines ORM models and API schemas
- `services.py` contains trade logic and the stochastic market simulator
- `auth.py` handles password hashing and bearer-token auth
- `tests/test_api.py` validates the public API surface against the local runtime

## Quick Start

### Docker

```bash
docker compose up --build
```

By default, the service is published on `http://localhost:18008`.

Swagger UI:

```text
http://localhost:18008/docs
```

Health check:

```text
http://localhost:18008/health
```

Stop the stack:

```bash
docker compose down
```

### Local Development

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the API:

```bash
uvicorn main:app --reload --port 18008
```

Run tests:

```bash
pytest -q
```

## Configuration

The service is configured through environment variables.

- `APP_PORT`
- `DATABASE_URL`
- `SECRET_KEY`
- `JWT_EXPIRE_MINUTES`
- `ADMIN_PASSWORD`
- `DAO_HUB_URL`
- `DAO_NODE_ID`

The shipped defaults are for local demo use only.

## Authentication

The API uses Bearer tokens.

1. Request a token from `POST /api/v1/auth/token`
2. Use the returned access token for protected endpoints

Seeded local credentials:

- username: `admin@energy.local`
- password: `changeme`

## Main Endpoints

Public endpoints:

- `GET /`
- `GET /health`
- `GET /api/v1/market/latest`
- `GET /api/v1/market/history`
- `POST /api/v1/optimize`
- `POST /api/v1/auth/token`

Protected endpoints:

- `POST /api/v1/trades`
- `GET /api/v1/trades`
- `GET /api/v1/trades/all`

## Relationship To DAO Hub

This repository is part of the approved Wave 2 naming set around DAO Hub.

Public narrative:

- DAO Hub is the ecosystem center
- DAO Renewable Energy Trading is a specialized energy-market node
- both were developed within Sampo AI OS

That structure lets the hub remain the flagship while this repo shows a concrete market-facing energy subsystem behind the broader governance and trading story.
