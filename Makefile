SRC_DIR=src

build-protobuf:
	poetry run python -m grpc_tools.protoc \
    -I src/protobufs \
    --python_out=$(SRC_DIR) \
    --grpc_python_out=$(SRC_DIR) \
    --mypy_out=$(SRC_DIR) \
    $(SRC_DIR)/protobufs/*/*.proto

mypy:
	poetry run mypy $(SRC_DIR)

flake:
	poetry run flake8 $(SRC_DIR)

black-lint:
	poetry run black --check $(SRC_DIR)

isort:
	poetry run isort $(SRC_DIR)

format: black isort

lint: flake mypy black-lint

cov:
	poetry run pytest --cov=$(SRC_DIR) $(SRC_DIR)

black:
	poetry run black $(SRC_DIR)

dev:
	docker compose up db redis -d

down:
	docker compose down

test:
	poetry run pytest $(SRC_DIR)

makemigrations:
	poetry run alembic revision --autogenerate --message $(message)
