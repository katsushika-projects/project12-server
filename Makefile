include .env
export $(shell sed 's/=.*//' .env)


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
	docker compose -f compose-dev.yml exec django mypy .


@.PHONY: bandit
bandit:
	docker compose -f compose-dev.yml exec django bandit -r .

.PHONY: check
check:
	@make ruff
	# @make mypy
	@make bandit
	@make test


# デプロイに関するコマンド

## ビルドするコマンド
.PHONY: gcp-build
gcp-build:
	docker build -t asia-northeast1-docker.pkg.dev/$(PROJECT_ID)/$(REPOSITORY)/django-app -f ./app/Dockerfile.prod ./app
## GCPにプッシュするコマンド
.PHONY: gcp-push
gcp-push:
	docker push asia-northeast1-docker.pkg.dev/$(PROJECT_ID)/$(REPOSITORY)/django-app
## .envファイルから .env.yamlを生成するコマンド
.PHONY: generate-env-yaml
generate-env-yaml:
	@echo "" > .env.yaml
	@grep -v -e '^PORT=' -e '^#' -e '^$$' .env | while IFS='=' read -r key val; do \
		cleaned_val=$$(echo $$val | sed 's/^"\(.*\)"$$/\1/'); \
		echo "$$key: \"$$cleaned_val\"" >> .env.yaml; \
	done
## GCPへdeployするコマンド
.PHONY: gcp-deploy
gcp-deploy:
	gcloud run deploy django-app \
	--image asia-northeast1-docker.pkg.dev/$(PROJECT_ID)/$(REPOSITORY)/django-app \
	--region asia-northeast1 \
	--platform managed \
	--allow-unauthenticated \
	--max-instances=1 \
	--project=$(PROJECT_ID) \
	--env-vars-file=.env.yaml \
	--add-cloudsql-instances=$(CLOUD_SQL_CONNECTION_NAME)


## まとめのコマンド
.PHONY: deploy
deploy:
	@echo "Starting deployment process..."
	@echo "Building Docker image..."
	@make gcp-build
	@echo "Pushing Docker image to GCP..."
	@make gcp-push
	@echo "Generating .env.yaml from .env..."
	@make generate-env-yaml
	@echo "Deploying to GCP..."
	@make gcp-deploy
