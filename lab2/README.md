# Lab 2: Docker Compose

## Overview

The project runs the Lab 1 Flask notes application with PostgreSQL as three Compose services:

- `database` provides PostgreSQL, persists data in `lab2-database-data`, and exposes a health check.
- `init` runs `init_db.py` once, creates the `notes` table, and exits successfully.
- `app` builds `Dockerfile` as `lab2-notes-api:latest`, runs the Flask API, and waits for both a healthy database and successful initialization.

All services use the shared `lab2-network` network. Containers have fixed names, and the application is published at `127.0.0.1:8000`.

## Configuration

Create the local environment file and adjust its values when necessary:

```bash
cd lab2
cp example.env .env
```

Change `DATABASE_PASSWORD` in `.env` before using the project outside local development.

## Run

```bash
docker compose up --build -d
curl http://127.0.0.1:8000/health
```

Stop the services with:

```bash
docker compose down
```

Add `--volumes` to also remove the PostgreSQL data volume.

## Questions

### Can CPU and memory limits be set for services in docker-compose.yml?

Yes. Current Docker Compose versions support resource limits through `deploy.resources.limits`:

```yaml
services:
  app:
    deploy:
      resources:
        limits:
          cpus: "0.50"
          memory: 512M
```

`cpus` limits CPU time and `memory` limits RAM usage. Legacy `docker-compose` versions may ignore `deploy` outside Swarm mode; in that case, upgrade Docker Compose or use the legacy resource options supported by the installed version. This probability supported by Linux cgroups kernel functions.

### How can only one service be started without starting the others?

Use an explicit service name:

```bash
docker compose up -d app
```

This starts `app` and its required `depends_on` services. To start only the named service without its dependencies, add `--no-deps`:

```bash
docker compose up -d --no-deps app
```

For an already created but stopped container, use `docker compose start app`.
