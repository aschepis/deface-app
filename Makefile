### CONFIG ####################################################################

CONDA_ENV := deface-build
CONDA_PY := 3.12
APP := Deface
SPEC := deface.spec
DIST_APP := dist/$(APP).app
SIGNING_IDENTITY ?= -

### INTERNAL ##################################################################

# Helper to run commands inside the conda environment
CONDA_RUN := conda run -n $(CONDA_ENV)

### TARGETS ###################################################################

.PHONY: help conda-env conda-remove install install-dev build build-macos sign \
        dist clean shell test lint format check

help:
	@echo "Conda-based build system for macOS Deface.app"
	@echo ""
	@echo "Available targets:"
	@echo "  make conda-env       Create the conda environment"
	@echo "  make install         Install runtime dependencies"
	@echo "  make install-dev     Install dev dependencies + pyinstaller"
	@echo "  make test            Run tests with coverage"
	@echo "  make lint            Run linting checks (flake8, black, isort, mypy)"
	@echo "  make format          Auto-format code with black and isort"
	@echo "  make check           Run tests and linting (fails on any error)"
	@echo "  make build-macos     Build macOS .app bundle"
	@echo "  make sign            Sign the .app (use SIGNING_IDENTITY=<id> for real signing)"
	@echo "  make dist            Create distributable .zip"
	@echo "  make shell           Enter the conda env shell"
	@echo "  make clean           Remove build output"
	@echo "  make conda-remove    Remove the conda env entirely"
	@echo ""
	@echo "Examples:"
	@echo "  make sign                                    # Ad-hoc signing (for local testing)"
	@echo "  make sign SIGNING_IDENTITY='Developer ID'   # Sign with Apple Developer ID"

### ENVIRONMENT MANAGEMENT ####################################################

conda-env:
	conda create -y -n $(CONDA_ENV) python=$(CONDA_PY)

conda-remove:
	conda remove -y --name $(CONDA_ENV) --all

shell:
	conda run -n $(CONDA_ENV) bash

### INSTALLATION ##############################################################

install:
	$(CONDA_RUN) pip install --upgrade pip
	$(CONDA_RUN) pip install -r requirements.txt

install-dev: install
	$(CONDA_RUN) pip install -r requirements-dev.txt
	$(CONDA_RUN) pip install pyinstaller

### TESTING ###################################################################

test:
	$(CONDA_RUN) pytest tests/ -v

### CODE QUALITY ###############################################################

lint:
	@echo "→ Running flake8..."
	$(CONDA_RUN) flake8 main.py tests/
	@echo "→ Running black (check mode)..."
	$(CONDA_RUN) black --check main.py tests/
	@echo "→ Running isort (check mode)..."
	$(CONDA_RUN) isort --check-only main.py tests/
	@echo "→ Running mypy..."
	$(CONDA_RUN) mypy main.py
	@echo "✓ All linting checks passed!"

format:
	@echo "→ Running black..."
	$(CONDA_RUN) black main.py tests/
	@echo "→ Running isort..."
	$(CONDA_RUN) isort main.py tests/
	@echo "✓ Code formatted!"

check: test lint
	@echo ""
	@echo "✓ All checks passed!"

### BUILDING ##################################################################

build: build-macos

build-macos:
	$(CONDA_RUN) python -m PyInstaller $(SPEC)

### SIGNING ###################################################################

sign:
	@echo "→ Signing $(DIST_APP) with identity: $(SIGNING_IDENTITY)"
	codesign --force --deep --sign "$(SIGNING_IDENTITY)" $(DIST_APP)
	@echo "✓ Signing complete!"

### PACKAGING #################################################################

dist:
	mkdir -p dist-packages
	cd dist && zip -r ../dist-packages/$(APP)-macos.zip $(APP).app
	@echo "→ Distribution package: dist-packages/$(APP)-macos.zip"

### CLEANUP ###################################################################

clean:
	rm -rf build dist __pycache__ *.egg-info
	find . -name "__pycache__" -exec rm -rf {} +
