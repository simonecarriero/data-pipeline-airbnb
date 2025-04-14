FROM python:3.12

WORKDIR /app
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
COPY pyproject.toml ./
COPY uv.lock ./
RUN uv sync --frozen --no-cache --no-dev
COPY airbnb.py airbnb.py
COPY definitions.py definitions.py
ENTRYPOINT ["uv", "run", "--no-dev", "dagster", "dev", "-h", "0.0.0.0", "-f", "definitions.py"]
