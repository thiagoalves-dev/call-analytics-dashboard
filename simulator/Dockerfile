FROM python:3.12-slim
COPY --from=ghcr.io/astral-sh/uv:0.10.10 /uv /usr/local/bin/uv
ENV UV_COMPILE_BYTECODE=1 UV_PROJECT_ENVIRONMENT=/opt/venv PATH="/opt/venv/bin:$PATH" PYTHONUNBUFFERED=1
WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-install-project
COPY simulator ./simulator
CMD ["python", "-m", "simulator"]
