# Stage 1: Builder
FROM ghcr.io/astral-sh/uv:python3.13-trixie-slim AS builder

ENV UV_PROJECT_ENVIRONMENT=/app

WORKDIR /src

COPY pyproject.toml uv.lock README.md ./

RUN --mount=type=cache,target=/root/.cache/uv \
  uv sync --locked --no-install-project --no-dev

COPY . .

RUN --mount=type=cache,target=/root/.cache/uv \
  uv sync --locked --no-dev --no-editable

# Stage 2: Runtime
FROM python:3.13-slim-trixie

COPY --from=builder /app /app

WORKDIR /app

EXPOSE 8080

CMD ["/app/bin/ai-chat"]
