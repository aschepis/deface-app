.PHONY: help install install-dev test lint format clean build build-windows build-macos build-linux dist installer-windows

# Default Python interpreter
PYTHON := python3
PY := $(PYTHON)

# Detect OS
UNAME_S := $(shell uname -s 2>/dev/null || echo "Linux")
ifeq ($(UNAME_S),Linux)
    PLATFORM := linux
endif
ifeq ($(UNAME_S),Darwin)
    PLATFORM := macos
endif
ifeq ($(OS),Windows_NT)
    PLATFORM := windows
endif

help: ## Show this help message
	@echo "Available targets:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install production dependencies
	$(PY) -m pip install --upgrade pip
	$(PY) -m pip install -r requirements.txt

install-dev: ## Install development dependencies
	$(PY) -m pip install --upgrade pip
	$(PY) -m pip install -r requirements-dev.txt
	$(PY) -m pip install -e .

test: ## Run tests with coverage
	$(PY) -m pytest tests/ -v

test-coverage: test ## Run tests and show coverage report
	@echo "Coverage report generated in htmlcov/index.html"

lint: ## Run all linting checks
	@echo "Running flake8..."
	$(PY) -m flake8 gui_run_deface.py tests/
	@echo "Running black check..."
	$(PY) -m black --check gui_run_deface.py tests/
	@echo "Running isort check..."
	$(PY) -m isort --check-only gui_run_deface.py tests/
	@echo "Running mypy..."
	$(PY) -m mypy gui_run_deface.py || true

format: ## Auto-format code with black and isort
	$(PY) -m black gui_run_deface.py tests/
	$(PY) -m isort gui_run_deface.py tests/
	@echo "Code formatted successfully"

clean: ## Remove build artifacts
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	rm -rf .pytest_cache
	rm -rf .mypy_cache
	rm -rf htmlcov/
	rm -rf .coverage
	rm -rf *.spec.bak
	rm -rf Output/
	find . -type d -name __pycache__ -exec rm -r {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true

build: ## Build executable for current platform
	@echo "Building for $(PLATFORM)..."
	$(PY) -m PyInstaller pyinstaller.spec --clean

build-windows: ## Build Windows executable
	@echo "Building Windows executable..."
	$(PY) -m PyInstaller pyinstaller.spec --clean --noconfirm

build-macos: ## Build macOS app bundle
	@echo "Building macOS app bundle..."
	$(PY) -m PyInstaller pyinstaller.spec --clean --noconfirm
	@echo "Note: To create .app bundle, you may need to modify pyinstaller.spec"

build-linux: ## Build Linux executable
	@echo "Building Linux executable..."
	$(PY) -m PyInstaller pyinstaller.spec --clean --noconfirm

dist: build ## Create distribution packages
	@echo "Creating distribution packages..."
	@mkdir -p dist-packages
ifeq ($(PLATFORM),macos)
	@echo "Creating macOS distribution..."
	cd dist && zip -r ../dist-packages/Deface-macos.zip Deface.app 2>/dev/null || zip -r ../dist-packages/Deface-macos.zip Deface
endif
ifeq ($(PLATFORM),linux)
	@echo "Creating Linux distribution..."
	cd dist && tar -czf ../dist-packages/Deface-linux.tar.gz Deface
endif
ifeq ($(PLATFORM),windows)
	@echo "Windows distribution should be created with installer-windows target"
endif
	@echo "Distribution packages created in dist-packages/"

installer-windows: build-windows ## Build Windows installer (requires Inno Setup)
	@echo "Building Windows installer..."
	@if command -v iscc >/dev/null 2>&1; then \
		iscc build_win_installer.iss; \
	else \
		echo "Error: Inno Setup Compiler (iscc) not found in PATH"; \
		echo "Please install Inno Setup from https://jrsoftware.org/isinfo.php"; \
		exit 1; \
	fi

check: lint test ## Run all checks (lint + test)

ci: install-dev lint test ## Run CI pipeline locally

