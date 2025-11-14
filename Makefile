### CONFIG ####################################################################

CONDA_ENV := deface-build
CONDA_PY := 3.12
APP := Deface
SPEC := deface.spec
DIST_APP := dist/$(APP).app

### INTERNAL ##################################################################

# Helper to run commands inside the conda environment
CONDA_RUN := conda run -n $(CONDA_ENV)

### TARGETS ###################################################################

.PHONY: help conda-env conda-remove install install-dev build build-macos sign \
        dist clean shell

help:
	@echo "Conda-based build system for macOS Deface.app"
	@echo ""
	@echo "Available targets:"
	@echo "  make conda-env       Create the conda environment"
	@echo "  make install         Install runtime dependencies"
	@echo "  make install-dev     Install dev dependencies + pyinstaller"
	@echo "  make build-macos     Build macOS .app bundle"
	@echo "  make sign            Ad-hoc sign the .app"
	@echo "  make dist            Create distributable .zip"
	@echo "  make shell           Enter the conda env shell"
	@echo "  make clean           Remove build output"
	@echo "  make conda-remove    Remove the conda env entirely"

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

### BUILDING ##################################################################

build: build-macos

build-macos:
	$(CONDA_RUN) python -m PyInstaller $(SPEC)

### SIGNING ###################################################################

sign:
	codesign --force --deep --sign - $(DIST_APP)

### PACKAGING #################################################################

dist:
	mkdir -p dist-packages
	cd dist && zip -r ../dist-packages/$(APP)-macos.zip $(APP).app
	@echo "→ Distribution package: dist-packages/$(APP)-macos.zip"

### CLEANUP ###################################################################

clean:
	rm -rf build dist __pycache__ *.egg-info
	find . -name "__pycache__" -exec rm -rf {} +
