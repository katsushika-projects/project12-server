.PHONY: dev-build
dev-build:
	docker compose -f compose-dev.yml build

.PHONY: dev-up-d
dev-up-d:
	docker compose -f compose-dev.yml up -d

.PHONY: dev
dev:
	@make dev-build
	@make dev-up-d

.PHONY: down
down:
	docker compose -f compose-dev.yml down

.PHONY: bash
bash:
	docker compose -f compose-dev.yml exec django bash

.PHONY: logs
logs:
	docker compose -f compose-dev.yml logs

.PHONY: test
test:
	docker compose -f compose-dev.yml exec django python manage.py test

# pythonコードのリント
.PHONY: ruff-check
ruff-check:
	docker compose -f compose-dev.yml exec django ruff check --fix .

# pythonコードのフォーマット
.PHONY: ruff-format
ruff-format:
	docker compose -f compose-dev.yml exec django ruff format .

# pythonコードのフォーマットとリント
.PHONY: ruff
ruff:
	@make ruff-check
	@make ruff-format

# pythonコードの静的解析
@.PHONY: mypy
mypy:
	docker compose -f compose-dev.yml exec django mypy --strict .


@.PHONY: bandit
bandit:
	docker compose -f compose-dev.yml exec django bandit -r .

.PHONY: check
check:
	@make ruff
	@make mypy
	@make bandit
	@make test

