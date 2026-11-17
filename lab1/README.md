# Lab 1: Bad and Good Dockerfiles

## Overview

This lab builds the same Flask application with two Dockerfiles:

- `Dockerfile.bad` demonstrates common Dockerfile mistakes.
- `Dockerfile.good` applies practices that make the image smaller, safer, and more predictable.

The API listens on port `8000` and stores notes under `/data`, which is intended to be mounted as a volume. The file-based storage can be replaced with a database in a later lab, while `/health` can be used for Kubernetes health probes.

## Repository

Repository: `<team repository URL>`

Replace the placeholder with the team's Git repository URL before submission.

## Project structure

```text
lab1/
|-- .dockerignore
|-- Dockerfile.bad
|-- Dockerfile.good
|-- README.md
|-- app.py
`-- requirements.txt
```

## API

| Method | Endpoint | Description |
| --- | --- | --- |
| `GET` | `/health` | Returns `{"status": "ok"}`. |
| `GET` | `/notes` | Returns all saved notes. |
| `POST` | `/notes` | Saves a note supplied as a JSON object with a `message` field. |

Notes are stored in the directory specified by `DATA_DIR`, which defaults to `/data`.

## Build and run the bad image

Build the image:

```bash
docker build -f Dockerfile.bad -t lab1-app:bad .
```

Create a named volume and start the container:

```bash
docker volume create lab1-bad-data
docker run --rm --name lab1-bad \
  -p 127.0.0.1:8001:8000 \
  -v lab1-bad-data:/data \
  lab1-app:bad
```

In another terminal, test the API:

```bash
curl http://127.0.0.1:8001/health

curl -X POST http://127.0.0.1:8001/notes \
  -H "Content-Type: application/json" \
  -d '{"message":"A note stored in the mounted volume."}'

curl http://127.0.0.1:8001/notes
```

The image should work normally. The problems in `Dockerfile.bad` are related to reproducibility, security, image size, caching, and maintainability—not application functionality.

## Problems in `Dockerfile.bad`

`Dockerfile.bad` intentionally demonstrates six common mistakes.

### 1. Using a mutable base image

It uses `python:latest`, which does not pin the Python version or the underlying operating system. Rebuilding the image later may therefore produce a different result.

`Dockerfile.good` uses the specific `python:3.12.4-slim-bookworm` tag instead.

### 2. Copying the entire build context

The instruction `COPY . .` copies everything in the build context, including files the application does not need and potentially sensitive local files. Changes to unrelated files can also invalidate the build cache.

The good Dockerfile copies only `requirements.txt` and `app.py`. The `.dockerignore` file excludes Git data, virtual environments, caches, generated Python files, and local volume data.

### 3. Installing unnecessary packages

The bad image installs `curl`, `vim`, `nano`, `gcc`, and `build-essential`. The application does not need these tools at runtime, so they only increase image size and the number of packages that need maintenance.

The good image uses a slim Python base and does not install unnecessary system packages.

### 4. Keeping the APT package cache

The bad Dockerfile installs packages without removing `/var/lib/apt/lists/*`, leaving package metadata in the final image.

The good Dockerfile does not need system packages. If they are added later, install them and remove the APT lists in the same `RUN` instruction.

### 5. Not pinning Python dependencies

The bad Dockerfile runs `pip install Flask`, so a rebuild may install a different Flask version.

The good Dockerfile installs the version pinned in `requirements.txt` (`Flask==3.0.3`) and uses `--no-cache-dir` to avoid retaining pip's download cache.

### 6. Running as root

Without a `USER` instruction, the application runs as root inside the container.

The good Dockerfile creates an unprivileged user with UID and GID `10001`, gives it write access to `/data`, and runs the application as that user.

## What `Dockerfile.good` changes

The good Dockerfile uses:

- A specific, slim base image.
- Explicit copying of only the required application files.
- A pinned Python dependency.
- No pip download cache.
- A non-root runtime user.
- A dedicated writable `/data` directory.
- Environment variables for runtime configuration.
- A Docker health check that calls `/health`.
- An entry point that sends logs to standard output.

## Build and run the good image

A volume is required for this lab so that notes persist after the container is removed. The examples use a named volume for this purpose.

Build the image and start the container:

```bash
docker build -f Dockerfile.good -t lab1-app:good .
docker volume create lab1-good-data
docker run --rm --name lab1-good \
  -p 127.0.0.1:8000:8000 \
  -v lab1-good-data:/data \
  lab1-app:good
```

Save a note:

```bash
curl -X POST http://127.0.0.1:8000/notes \
  -H "Content-Type: application/json" \
  -d '{"message":"Persistent data survives container replacement."}'
```

To check persistence, stop the container and start another one using the same volume:

```bash
docker rm -f lab1-good

docker run --rm --name lab1-good-again \
  -p 127.0.0.1:8000:8000 \
  -v lab1-good-data:/data \
  lab1-app:good

curl http://127.0.0.1:8000/notes
```

The saved note should still be there.

If you need to access the files directly from the host, use a bind mount instead:

```bash
docker run --rm --name lab1-good \
  -p 127.0.0.1:8000:8000 \
  -v "$(pwd)/data:/data" \
  lab1-app:good
```

## Two practices to avoid when running containers

### 1. Granting unnecessary privileges

Do not run this application with `--privileged`, mount the Docker socket, or add Linux capabilities it does not need:

```bash
docker run --privileged lab1-app:good
```

The application only needs to read and write `/data`. It does not need access to host devices, kernel features, or the Docker daemon. Use the default capability set and add privileges only when a specific requirement calls for them.

### 2. Exposing an unauthenticated API on every interface

Avoid publishing the API on all host interfaces:

```bash
docker run -p 8000:8000 lab1-app:good
```

Because the API has no authentication, any client that can reach the host may be able to read or create notes. For local development, bind it to loopback:

```bash
-p 127.0.0.1:8000:8000
```

Before exposing the API to other networks, add authentication, TLS, and appropriate network and ingress restrictions.

## When containers may not be the right choice

### 1. Direct hardware access and hard real-time workloads

Containers may be unsuitable when an application requires direct kernel-module control, specialized hardware behavior, or deterministic hard real-time scheduling. Examples include some industrial control systems, motor-control applications, and device drivers. Bare-metal execution or a suitably configured real-time operating system may provide more predictable behavior.

### 2. Strong isolation for untrusted workloads

Containers share the host kernel, so they do not provide the same isolation boundary as virtual machines. If mutually untrusted tenants need to run arbitrary code, virtual machines or dedicated hosts may be a safer choice. A container-based approach should be used only with an additional sandboxing layer that provides the required isolation.
