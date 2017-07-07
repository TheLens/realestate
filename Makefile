
.PHONY: help docs install test setup

.DEFAULT_GOAL := help

help: ## Prints help list for targets.
	@# http://marmelab.com/blog/2016/02/29/auto-documented-makefile.html
	@# Put help descriptions like shown above.
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

docs:  ## Build documentation.
	@cd docs && make html

test:  ## Run tests and produce coverage report.
	@coverage run --source=scripts,www -m unittest
	@coverage report -m

install:  ## Install all dependencies.
	@pip install -r requirements.txt
	@npm install

setup:  ## Install dependencies and run tests.
	@$(MAKE) install
	@$(MAKE) test
