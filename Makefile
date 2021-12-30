PROJECT := rps
CONDA_ENV := rps


env: environment.yml
	conda env create -n $(PROJECT) -f environment.yml

.PHONY: clean
clean:
	rm -rf ./build ./dist ./*egg-info
	find . -type f -name '*.pyc' -delete
	find . -type d -name '__pycache__' -delete
