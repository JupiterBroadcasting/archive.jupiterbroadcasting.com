help:
		@echo "Jupiter Broadcasting Archive Hugo Project"
		@echo
		@echo "Help for using this Makefile"
		@echo
		@echo "For detailed help about this project please visit:"
		@echo "https://github.com/goodwinlabs/archive.jupiterbroadcasting.com"
		@echo
		@echo "------------------------------------------------------------------"
		@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort  | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m - %s\n", $$1, $$2}'

dev-build: ## Generate the development docker container
	docker build --rm -f Dockerfile.dev -t jb_hugo:latest .

dev: dev-build ## Run the development hugo container
	docker run --rm -it -v "$${PWD}":/app -w /app -p $${HOST_IP:-127.0.0.1}:1313:1313 jb_hugo:latest

THEME_DIR ?= ../jb-hugo-theme
THEME_MODULE := github.com/goodwinlabs/jb-hugo-theme
# mounts the parent folder so the sibling theme checkout is visible inside the container
DEV_THEME_RUN = docker run --rm -it -v "$$(cd .. && pwd)":/work -w /work/$(notdir $(CURDIR)) \
	-e HUGO_MODULE_REPLACEMENTS="$(THEME_MODULE) -> /work/$(notdir $(abspath $(THEME_DIR)))" \
	-p $${HOST_IP:-127.0.0.1}:1313:1313 jb_hugo:latest

dev-theme: dev-build ## Run the development hugo container against a local jb-hugo-theme checkout (THEME_DIR, default ../jb-hugo-theme)
	$(DEV_THEME_RUN) serve -D --bind 0.0.0.0

dev-tests-theme: dev-build ## Like dev-tests, against a local jb-hugo-theme checkout
	$(DEV_THEME_RUN) serve -D --bind 0.0.0.0 --disableFastRender

dev-metrics: dev-build ## Run the development hugo container with metrics
	docker run --rm -it -v "$${PWD}":/app -w /app -p $${HOST_IP:-127.0.0.1}:1313:1313 jb_hugo:latest serve -D --bind 0.0.0.0 --templateMetrics --templateMetricsHints

dev-tests: dev-build ## Run the development hugo container with every page pre-rendered (for `make tests` with parallel workers)
	docker run --rm -it -v "$${PWD}":/app -w /app -p $${HOST_IP:-127.0.0.1}:1313:1313 jb_hugo:latest serve -D --bind 0.0.0.0 --disableFastRender

deploy-prod: ## Deploy everything to production
	docker build -t jb-archive .
	docker compose -f ~/docker-compose.yml up -d --force-recreate jb-archive
	# docker-compose.yml located on the production host, not within this repo.
	docker image prune -af

tests: ## Run the test suite (serve the site with `make dev-tests` first)
	docker build --rm -f Dockerfile.tests -t jb_tests:latest .
	if [ -d screenshots ]; then rm -rf screenshots/; fi
	docker run --rm --net=host --user 1000:1000 --volume "$${PWD}":/app -w /app jb_tests:latest
