# Makefile for Python project

# Define the Python interpreter
PYTHON := python

# Detect the operating system
ifeq ($(OS),Windows_NT)
    VENV_ACTIVATE := .\venv\Scripts\activate
    RM := del /q
else
    VENV_ACTIVATE := ./venv/bin/activate
    RM := rm -rf
endif

# Name of the virtual environment
VENV := venv

# Requirements file
REQUIREMENTS := requirements.txt

.PHONY: help venv install clean run

help:
	@echo "Please use 'make <target>' where <target> is one of"
	@echo "  venv       to create a virtual environment"
	@echo "  install    to install dependencies"
	@echo "  clean      to remove the virtual environment"
	@echo "  run        to run the project"

venv:
	@echo "Creating virtual environment..."
	$(PYTHON) -m venv $(VENV)

init: venv
	@echo "Installing dependencies..."
	$(VENV_ACTIVATE) && pip install -r $(REQUIREMENTS)

clean:
	@echo "Cleaning up..."
	$(RM) $(VENV)

run:
	@echo "Running project..."
	$(VENV_ACTIVATE) && $(PYTHON) main.py

run-pulp:
	@echo "Running project..."
	$(VENV_ACTIVATE) && $(PYTHON) pulp_solver.py