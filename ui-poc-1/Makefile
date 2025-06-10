.PHONY: help venv deps run clean freeze

PYTHON = python3
VENV_DIR = .venv
VENV_ACTIVATE = $(VENV_DIR)/bin/activate
PIP = $(VENV_DIR)/bin/pip
REQUIREMENTS = requirements.txt

help:
	@echo "Photo Tools GUI - Available targets:"
	@echo "  make venv      - Create virtual environment"
	@echo "  make deps      - Install dependencies from requirements.txt"
	@echo "  make run       - Run the application (creates venv and installs deps if needed)"
	@echo "  make clean     - Remove virtual environment"
	@echo "  make freeze    - Output current pip packages to requirements.txt"

venv:
	$(PYTHON) -m venv $(VENV_DIR)
	@echo "Virtual environment created in $(VENV_DIR)"

deps: venv
	$(PIP) install --upgrade pip
	$(PIP) install -r $(REQUIREMENTS)
	@echo "Dependencies installed"

run: deps
	$(VENV_DIR)/bin/python main.py

clean:
	rm -rf $(VENV_DIR)
	@echo "Virtual environment removed"

freeze:
	$(PIP) freeze > $(REQUIREMENTS)
	@echo "Requirements frozen to $(REQUIREMENTS)"
