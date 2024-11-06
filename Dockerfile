ARG PYTHON_VERSION=3.10

FROM python:${PYTHON_VERSION}-slim-buster AS builder

ENV POETRY_VERSION=1.5.1

ENV PIP_DISABLE_PIP_VERSION_CHECK=on
ENV PIP_NO_CACHE_DIR=off
ENV PYTHONDONTWRITEBYTECODE=on
ENV PYTHONFAULTHANDLER=on
ENV PYTHONUNBUFFERED=on

RUN apt-get update
RUN apt-get install -y --no-install-recommends build-essential gcc curl

WORKDIR /app

RUN pip install "poetry==$POETRY_VERSION"

RUN python -m venv venv

COPY pyproject.toml .
COPY poetry.lock .

RUN poetry export --format=requirements.txt --without=dev | venv/bin/pip install -r /dev/stdin

FROM python:${PYTHON_VERSION}-slim

WORKDIR /app

# Install curl for healthchecking
RUN apt-get -y update && apt-get install -y --no-install-recommends curl

# Copy installed packages
COPY --from=builder /app/venv venv
ENV PATH="/app/venv/bin:$PATH"

# Copy application
COPY src .

# Build gRPC services
RUN python -m grpc_tools.protoc \
    -I protobufs \
    --python_out=. \
    --grpc_python_out=. \
    protobufs/services/**/**.proto
