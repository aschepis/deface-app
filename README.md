# deface-app

[![CI](https://github.com/aschepis/deface-app/workflows/CI/badge.svg)](https://github.com/aschepis/deface-app/actions)
[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

A cross-platform GUI application for blurring faces in images and videos using the [deface](https://github.com/ORB-HD/deface) library.

## Features

- 🖼️ **Image & Video Support**: Blur faces in both images and video files
- 🖥️ **Cross-Platform**: Works on Windows, macOS, and Linux
- 🎨 **Simple GUI**: Easy-to-use graphical interface built with CustomTkinter
- ⚡ **Fast Processing**: Powered by the efficient deface library
- 📦 **Standalone Builds**: Create standalone executables for easy distribution

## Requirements

- Python 3.8 or higher
- tkinter (usually included with Python, but may need separate installation on Linux)
- [deface](https://github.com/ORB-HD/deface) library
- CustomTkinter for the graphical interface

### System Dependencies

**tkinter** is required for CustomTkinter to work. Installation varies by platform:

- **macOS**: tkinter is included with Python by default. If you get a `ModuleNotFoundError: No module named '_tkinter'` error, you may need to reinstall Python or install Python via Homebrew with tkinter support.
- **Linux**: Install the `python3-tk` package:
  - Debian/Ubuntu: `sudo apt-get install python3-tk`
  - Fedora: `sudo dnf install python3-tkinter`
  - Arch: `sudo pacman -S tk`
- **Windows**: tkinter is included with Python by default.

## Installation

### Option 1: Install from Source

1. Clone the repository:

   ```bash
   git clone https://github.com/aschepis/deface-app.git
   cd deface-app
   ```

2. Create a virtual environment:

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Run the application:
   ```bash
   python main.py
   ```

### Option 2: Build Standalone Executable

1. Install PyInstaller:

   ```bash
   pip install pyinstaller
   ```

2. Build the executable:

   ```bash
   make build
   # Or manually:
   pyinstaller pyinstaller.spec
   ```

3. Run the executable:
   - **Windows**: `dist\Deface\Deface.exe`
   - **macOS/Linux**: `dist/Deface/Deface`

## Usage

1. Launch the application (either run the Python script or the executable)
2. Click "Browse" next to "Input image/video" and select your file
3. Click "Browse" next to "Output folder" and select where you want the processed file saved
4. Click "Run" to start processing
5. Monitor progress in the log window
6. The processed file will be saved in the output folder with the same filename

## Development

### Setup Development Environment

```bash
# Clone the repository
git clone https://github.com/aschepis/deface-app.git
cd deface-app

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
make install-dev
# Or manually:
pip install -r requirements-dev.txt
```

### Available Make Commands

- `make install` - Install production dependencies
- `make install-dev` - Install development dependencies
- `make test` - Run tests with coverage
- `make lint` - Run all linting checks (flake8, black, isort, mypy)
- `make format` - Auto-format code with black and isort
- `make build` - Build executable for current platform
- `make build-windows` - Build Windows executable
- `make build-macos` - Build macOS app bundle
- `make build-linux` - Build Linux executable
- `make clean` - Remove build artifacts
- `make dist` - Create distribution packages
- `make check` - Run linting and tests
- `make ci` - Run CI pipeline locally

### Running Tests

```bash
make test
# Or manually:
pytest tests/ -v --cov=main --cov-report=html
```

### Code Quality

The project uses several tools to maintain code quality:

- **black**: Code formatting
- **flake8**: Linting
- **isort**: Import sorting
- **mypy**: Type checking (non-strict)
- **pytest**: Testing framework

Run all checks:

```bash
make lint
```

Auto-format code:

```bash
make format
```

## Building & Signing the macOS Application

This project uses a **Conda-based build environment** to produce a fully standalone, code-signable macOS `.app` bundle. To build and sign the application:

### **1. Create the Conda build environment**

```sh
make conda-env
```

### **2. Install dependencies (runtime + dev + PyInstaller)**

```sh
make install-dev
```

### **3. Build the macOS `.app` bundle**

```sh
make build-macos
```

The built application will appear at:

```
dist/Deface.app
```

### **4. Ad-hoc sign the app (for local use/testing)**

```sh
make sign
```

### **5. Package a distributable ZIP**

```sh
make dist
```

Output will be placed in:

```
dist-packages/Deface-macos.zip
```

### **6. Optional: Developer ID signing**

```sh
codesign --force --deep --options runtime \
  --sign "Developer ID Application: Your Name (TEAMID)" \
  dist/Deface.app
```

## Contributing

Contributions are welcome! Please read our [Contributing Guidelines](CONTRIBUTING.md) for details on:

- Code style and standards
- Development workflow
- Testing requirements
- Pull request process

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [deface](https://github.com/ORB-HD/deface) - The underlying face blurring library
- [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter) - The GUI framework
- [PyInstaller](https://www.pyinstaller.org/) - For creating standalone executables

## Troubleshooting

### ModuleNotFoundError: No module named '\_tkinter'

This error indicates that tkinter is not available. See the [System Dependencies](#system-dependencies) section above for installation instructions.

**macOS specific**: If you installed Python via Homebrew and tkinter is missing, try:

```bash
brew install python-tk
```

Or reinstall Python with tkinter support.

## Support

- **Issues**: Report bugs or request features on [GitHub Issues](https://github.com/aschepis/deface-app/issues)

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for a list of changes and version history.
