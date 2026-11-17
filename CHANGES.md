# ITMO 2026 Containers & Orch

## Lab 1 - Good and bad Dockerfiles

This lab explores Dockerfile best practices by comparing two Docker images for the same Flask application. It demonstrates common mistakes in container image construction and shows how to improve security, reproducibility, and efficiency through proper base image selection, dependency management, file handling, and non-root execution. It also covers persistent volume storage, secure container runtime configurations, and scenarios where containers may not be the best choice.

Changes made: 2026.11.07


## Lab2 - Docker Compose

Lab 2 adds a Docker Compose project containing a one-time database initialization service, a PostgreSQL service, and a Flask notes application. The services use a shared named network, fixed container names, health checks, a persistent database volume, and environment variables from .env.

Changes made: 2026.11.17