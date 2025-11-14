"""Configuration persistence manager for deface-app.

This module handles loading and saving application configuration to disk.
Uses platform-appropriate storage when possible, falls back to a JSON file
in the user's home directory.
"""

import json
import logging
import os
import sys
from pathlib import Path
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)

# Configuration file name (hidden file in home directory)
CONFIG_FILENAME = ".deface-app.json"


def get_config_path() -> Path:
    """Get the path to the configuration file.

    Uses platform-appropriate storage when possible:
    - macOS: ~/Library/Application Support/deface-app/config.json
    - Windows: %APPDATA%/deface-app/config.json
    - Linux: ~/.config/deface-app/config.json

    Falls back to ~/.deface-app.json if platform-specific paths aren't available.

    Returns:
        Path to the configuration file.
    """
    home = Path.home()

    # Try platform-specific paths first
    if sys.platform == "darwin":  # macOS
        config_dir = home / "Library" / "Application Support" / "deface-app"
        config_file = config_dir / "config.json"
    elif sys.platform == "win32":  # Windows
        appdata = os.environ.get("APPDATA")
        if appdata:
            config_dir = Path(appdata) / "deface-app"
            config_file = config_dir / "config.json"
        else:
            # Fallback to home directory
            config_file = home / CONFIG_FILENAME
    else:  # Linux and other Unix-like systems
        config_dir = home / ".config" / "deface-app"
        config_file = config_dir / "config.json"

    # Test if we can write to the platform-specific path
    try:
        # Try to create the directory if it doesn't exist
        if config_file.parent != home:
            config_file.parent.mkdir(parents=True, exist_ok=True)
        # Test if we can write to the directory
        test_file = config_file.parent / ".test_write"
        test_file.touch()
        test_file.unlink()
    except (OSError, PermissionError):
        # Fallback to home directory if platform-specific path isn't writable
        logger.debug(f"Could not use platform-specific config path, using fallback")
        config_file = home / CONFIG_FILENAME

    return config_file


def load_config() -> Dict[str, Any]:
    """Load configuration from disk.

    Returns:
        Dictionary containing configuration. Returns default configuration
        if file doesn't exist or cannot be read.
    """
    config_path = get_config_path()

    if not config_path.exists():
        logger.debug(f"Config file does not exist: {config_path}")
        return get_default_config()

    try:
        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)
        logger.info(f"Loaded configuration from: {config_path}")
        return config
    except (json.JSONDecodeError, IOError, OSError) as e:
        logger.warning(f"Error loading config from {config_path}: {e}")
        logger.info("Using default configuration")
        return get_default_config()


def save_config(config: Dict[str, Any]) -> bool:
    """Save configuration to disk.

    Args:
        config: Dictionary containing configuration to save.

    Returns:
        True if configuration was saved successfully, False otherwise.
    """
    config_path = get_config_path()

    try:
        # Ensure parent directory exists
        config_path.parent.mkdir(parents=True, exist_ok=True)

        # Write configuration to file
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2, ensure_ascii=False)

        logger.info(f"Saved configuration to: {config_path}")
        return True
    except (IOError, OSError) as e:
        logger.error(f"Error saving config to {config_path}: {e}")
        return False


def get_default_config() -> Dict[str, Any]:
    """Get default configuration values.

    Returns:
        Dictionary containing default configuration.
    """
    return {
        "deface_config": {
            "thresh": 0.2,
            "scale": None,
            "boxes": False,
            "mask_scale": 1.3,
            "replacewith": "blur",
            "keep_audio": True,
            "keep_metadata": True,
            "batch_size": 1,
        },
        "output_directory": None,  # Will default to Desktop on first run
    }

