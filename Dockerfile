# syntax=docker/dockerfile:1

ARG PYTHON_VERSION=3.13
FROM python:${PYTHON_VERSION}-slim as base

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

ENV UV_CACHE_DIR=/var/cache/uv

FROM base as builder

WORKDIR /app

COPY pyproject.toml uv.lock ./
COPY packages /app/packages
RUN --mount=type=cache,target=${UV_CACHE_DIR} \
    uv pip install . --system

FROM base

COPY --from=builder /usr/local/lib/python3.13/site-packages /usr/local/lib/python3.13/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

WORKDIR /app

ENTRYPOINT ["python"]
CMD ["-m", "hypercore_ca_distributor"]
