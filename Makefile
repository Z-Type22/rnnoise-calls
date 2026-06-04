init:
	docker compose build
	docker compose up -d
	docker compose exec fastapi /bin/sh -c 'echo "применяем миграции"'
	docker compose exec fastapi alembic upgrade head
	docker compose logs -f

build:
	docker compose build
	docker compose exec fastapi /bin/sh -c 'echo "применяем миграции"'
	docker compose exec fastapi alembic upgrade head

up:
	docker compose up -d --build
	docker compose exec fastapi /bin/sh -c 'echo "применяем миграции"'
	docker compose exec fastapi alembic upgrade head

migrate:
	docker compose exec fastapi /bin/sh -c 'echo "применяем миграции"'
	docker compose exec fastapi alembic upgrade head

down:
	docker compose down
