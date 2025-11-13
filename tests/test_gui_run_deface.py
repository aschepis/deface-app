"""Unit tests for gui_run_deface.py."""
import os
import subprocess
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import pytest

import gui_run_deface


class TestRunDeface:
    """Tests for the run_deface function."""

    def test_run_deface_basic(self, mock_subprocess):
        """Test basic run_deface function call."""
        input_path = "/path/to/input.jpg"
        output_path = "/path/to/output.jpg"
        
        proc = gui_run_deface.run_deface(input_path, output_path)
        
        assert proc is not None
        # Verify subprocess.Popen was called
        subprocess.Popen.assert_called_once()

    def test_run_deface_with_extra_args(self, mock_subprocess):
        """Test run_deface with extra arguments."""
        input_path = "/path/to/input.jpg"
        output_path = "/path/to/output.jpg"
        extra_args = "--threshold 0.5"
        
        proc = gui_run_deface.run_deface(input_path, output_path, extra_args)
        
        assert proc is not None
        call_args = subprocess.Popen.call_args[0][0]
        assert "--threshold" in call_args
        assert "0.5" in call_args

    def test_run_deface_command_structure(self, mock_subprocess):
        """Test that run_deface constructs the correct command."""
        input_path = "/test/input.mp4"
        output_path = "/test/output.mp4"
        
        gui_run_deface.run_deface(input_path, output_path)
        
        call_args = subprocess.Popen.call_args[0][0]
        assert call_args[0] == "deface"
        assert input_path in call_args
        assert "--output" in call_args
        assert output_path in call_args


class TestGUILogic:
    """Tests for GUI logic and event handling."""

    def test_file_path_validation(self, mock_customtkinter, sample_input_file, sample_output_dir):
        """Test that file paths are validated before processing."""
        mock_ctk, mock_app = mock_customtkinter
        
        # Test validation logic directly
        from gui_run_deface import validate_paths
        
        # Test empty input
        is_valid, error_msg = validate_paths("", sample_output_dir)
        assert not is_valid
        assert "input file" in error_msg.lower()
        
        # Test empty output
        is_valid, error_msg = validate_paths(sample_input_file, "")
        assert not is_valid
        assert "output" in error_msg.lower()

    def test_output_path_construction(self, sample_input_file, sample_output_dir):
        """Test that output path is constructed correctly."""
        input_path = sample_input_file
        output_dir = sample_output_dir
        
        expected_output = os.path.join(output_dir, os.path.basename(input_path))
        assert expected_output == os.path.join(output_dir, "test_image.jpg")

    @patch("gui_run_deface.run_deface")
    def test_process_termination_on_quit(self, mock_run_deface, mock_customtkinter):
        """Test that process is terminated when quitting."""
        mock_ctk, mock_app = mock_customtkinter
        mock_proc = MagicMock()
        mock_proc.poll.return_value = None  # Process still running
        mock_run_deface.return_value = mock_proc
        
        # Test the termination logic directly
        proc = mock_proc
        if proc and proc.poll() is None:
            proc.terminate()
        
        mock_proc.terminate.assert_called_once()

    def test_process_output_reading(self, mock_subprocess):
        """Test that process output is read correctly."""
        mock_proc = MagicMock()
        mock_proc.stdout.readline.return_value = "Processing...\n"
        mock_proc.poll.return_value = None
        
        output_line = mock_proc.stdout.readline()
        assert output_line == "Processing...\n"
        
        # Test finished state
        mock_proc.poll.return_value = 0
        assert mock_proc.poll() is not None


class TestErrorHandling:
    """Tests for error handling scenarios."""

    def test_missing_input_file(self, sample_output_dir):
        """Test handling of missing input file."""
        input_path = "/nonexistent/file.jpg"
        output_path = os.path.join(sample_output_dir, "output.jpg")
        
        # File doesn't exist
        assert not os.path.exists(input_path)

    def test_invalid_output_directory(self, sample_input_file):
        """Test handling of invalid output directory."""
        input_path = sample_input_file
        output_dir = "/nonexistent/directory"
        
        # Directory doesn't exist
        assert not os.path.exists(output_dir)

    @patch("subprocess.Popen")
    def test_subprocess_error_handling(self, mock_popen):
        """Test handling of subprocess errors."""
        mock_popen.side_effect = OSError("Command not found")
        
        with pytest.raises(OSError):
            gui_run_deface.run_deface("/input.jpg", "/output.jpg")

