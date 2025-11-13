"""Pytest configuration and fixtures."""
import os
import sys
from pathlib import Path
from unittest.mock import MagicMock

import pytest

# Add parent directory to path for imports
parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir))


@pytest.fixture
def mock_subprocess(monkeypatch):
    """Mock subprocess.Popen for testing."""
    mock_proc = MagicMock()
    mock_proc.stdout.readline.return_value = ""
    mock_proc.poll.return_value = 0
    mock_proc.stderr = MagicMock()
    mock_proc.stdout = MagicMock()
    
    def mock_popen(*args, **kwargs):
        return mock_proc
    
    monkeypatch.setattr("subprocess.Popen", mock_popen)
    return mock_proc


@pytest.fixture
def mock_customtkinter(monkeypatch):
    """Mock CustomTkinter for testing."""
    mock_ctk = MagicMock()
    mock_app = MagicMock()
    mock_app.mainloop = MagicMock()
    mock_app.after = MagicMock()
    mock_app.protocol = MagicMock()
    mock_app.destroy = MagicMock()
    mock_app.input_entry = MagicMock()
    mock_app.output_entry = MagicMock()
    mock_app.log_textbox = MagicMock()
    mock_app.run_btn = MagicMock()
    mock_app.proc = None
    
    # Mock CTk class to return our mock app
    mock_ctk.CTk = MagicMock(return_value=mock_app)
    mock_ctk.CTkFrame = MagicMock()
    mock_ctk.CTkLabel = MagicMock()
    mock_ctk.CTkEntry = MagicMock()
    mock_ctk.CTkButton = MagicMock()
    mock_ctk.CTkTextbox = MagicMock()
    mock_ctk.CTkFont = MagicMock()
    mock_ctk.set_appearance_mode = MagicMock()
    mock_ctk.set_default_color_theme = MagicMock()
    
    monkeypatch.setattr("gui_run_deface.ctk", mock_ctk)
    return mock_ctk, mock_app


@pytest.fixture
def sample_input_file(tmp_path):
    """Create a sample input file for testing."""
    test_file = tmp_path / "test_image.jpg"
    test_file.write_bytes(b"fake image data")
    return str(test_file)


@pytest.fixture
def sample_output_dir(tmp_path):
    """Create a sample output directory for testing."""
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    return str(output_dir)

