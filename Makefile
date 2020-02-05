all: install_dev

install:
	pip install -r requirements.txt

install_dev:
	pip install -r requirements-dev.txt

lint:
	flake8 pipeos_contracts/

compile:
	python setup.py compile_contracts
