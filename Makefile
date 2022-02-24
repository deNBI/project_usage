up-dev:  ## Run bin/project_usage-compose.py dev up --detach
	bin/project_usage-compose.py dev up --detach

down-dev: ## Run bin/project_usage-compose.py dev down
	bin/project_usage-compose.py dev down

logs-credits: ## Follows logs of portal_credits
	docker logs -f portal_credits

enter-db: ## Enters timescale db docker container
	docker exec -it portal_timescaledb bash -c "psql -U postgres"

help:
	    @egrep '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-16s\033[0m %s\n", $$1, $$2}'

.PHONY: help