
VERSION := latest

ENV_DIR := .venv

all: build start venv

venv:
	@echo "+++ Setting up virtual environment +++"
	python3 -m venv $(ENV_DIR)
	$(ENV_DIR)/bin/pip install --upgrade pip
	$(ENV_DIR)/bin/pip install -r requirements.txt

rename:
	@echo "+++ Running photo-renamer.py +++"
	$(ENV_DIR)/bin/python photo-renamer.py

filter:
	@echo "+++ Running photo-filter.py +++"
	$(ENV_DIR)/bin/python photo-filter.py

process:
	@echo "+++ Running photo-processor.py +++"
	$(ENV_DIR)/bin/python photo-processor.py

# Docker-ized image

build:
	@echo "+++ Building docker image +++"
	docker build --pull --build-arg VERSION=$(VERSION) -t kalemena/photo-tools:$(VERSION) .

start:
	docker run -it --rm -v $(pwd):/projects kalemena/photo-tools:$(VERSION) bash
