FROM python:3.12-slim

WORKDIR /app

RUN apt update \
    && apt install -y postgresql-client \
    && apt clean \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml poetry.lock* ./

RUN pip install --upgrade pip && pip install poetry \
    && poetry config virtualenvs.create false \
    && poetry install --no-root --no-interaction --no-ansi

COPY . .
