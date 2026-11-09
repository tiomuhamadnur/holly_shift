COMPOSE ?= docker compose
WEB ?= web
MANAGE = $(COMPOSE) exec $(WEB) python manage.py
TAILWIND ?= tailwindcss

.PHONY: dev prod test lint check migrate migrations-check seed css backup messages shell audit

dev:
	$(COMPOSE) up

prod:
	$(COMPOSE) -f docker-compose.prod.yml up -d

test:
	$(COMPOSE) exec $(WEB) pytest --cov=apps --cov-report=term-missing

lint:
	$(COMPOSE) exec $(WEB) ruff check .

migrations-check:
	$(MANAGE) makemigrations --check --dry-run

i18n-check:
	$(MANAGE) check_i18n

check: lint test migrations-check i18n-check

migrate:
	$(MANAGE) migrate

seed:
	$(MANAGE) seed_roles
	$(MANAGE) seed_settings

css:
	$(TAILWIND) -i static/css/input.css -o static/css/app.css --minify

backup:
	$(COMPOSE) exec -T db sh -c 'pg_dump -U "$$POSTGRES_USER" "$$POSTGRES_DB"' > backup.sql

messages:
	$(MANAGE) makemessages -l id -l en --ignore=.venv --ignore=staticfiles

shell:
	$(MANAGE) shell

audit:
	$(COMPOSE) exec $(WEB) pip-audit -r requirements/dev.txt
