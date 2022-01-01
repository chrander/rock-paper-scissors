.ONESHELL:

help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'


PROJECT_NAME := rps
CONDA_ENV := rps
TEST_DIR := ./tests
SOURCE_DIR := ./rps
MAX_LINE_LEN := 120

# Need to specify bash in order for conda activate to work.
SHELL=/bin/bash
# Note that the extra activate is needed to ensure that the activate floats env to the front of PATH
CONDA_ACTIVATE=source $$(conda info --base)/etc/profile.d/conda.sh ; conda activate ; conda activate

.PHONY: env
env: environment.yml
	conda env create -n $(PROJECT_NAME) -f environment.yml

.PHONY: cleanenv
cleanenv:
	conda deactivate && conda env remove -n $(PROJECT_NAME)

.PHONY: clean
clean:
	rm -rf ./build ./dist ./*egg-info
	find . -type f -name '*.pyc' -delete
	find . -type d -name '__pycache__' -delete

.PHONY: run
run: run.py
	$(CONDA_ACTIVATE) $(CONDA_ENV)
	python run.py

.PHONY: format
format: ## Run all python code through the autopep8 formatter and isort
	$(CONDA_ACTIVATE) $(CONDA_ENV)
	python -m pip install autoflake==1.3.1 autopep8==1.5.3 isort==5.1.4
	python -m autopep8 -vv --in-place --recursive --max-line-length $(MAX_LINE_LEN) --aggressive $(SOURCE_DIR)
	python -m autoflake --in-place --remove-all-unused-imports -r $(SOURCE_DIR)
	python -m isort --verbose --apply --recursive $(SOURCE_DIR)

.PHONY: build
build: ## Run all python code through Static Analysis
	$(CONDA_ACTIVATE) $(CONDA_ENV)
	python -m pip install flake8==3.8.3
	python -m flake8 --verbose --statistics --max-complexity 10 --max-line-length $(MAX_LINE_LEN) $(SOURCE_DIR)/*.py
	#mypy --implicit-reexport --ignore-missing-imports -p $(PROJECT_NAME)

.PHONY: test
test: ## Run all tests
	$(CONDA_ACTIVATE) $(CONDA_ENV)
	python -m pytest -v --cache-clear --cov-report term --cov-report html:coverage --cov $(SOURCE_DIR) $(TEST_DIR)/
