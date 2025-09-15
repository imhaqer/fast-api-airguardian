
# Stage 1: build dependencies
FROM python:3.13-slim AS builder

RUN apt-get update && apt-get install -y \
    curl \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

RUN curl -sSh  -sSL https://install.python-poetry.org | python3 -

ENV PATH="/root/.local/bin:$PATH" \
    POETERY_VIRTUALENVS_CREATE=false \
    POETRY_NO_INTERACTION=1

WORKDIR /app

COPY pyproject.toml poetry.lock* /app/

RUN poetry install --no-root --no-interaction --no-ansi


# Stage 2: runtime
FROM python:3.13-slim
RUN apt-get update && apt-get install -y \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

copy --from=builder /usr/local /usr/local
COPY src ./src

EXPOSE 8000

CMD ["poerty", "run", "fastapi", "dev", "src/fast_api_airguardian/main.py", "--host", "0.0.0.0", "--port", "8000"]