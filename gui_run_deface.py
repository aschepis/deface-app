"""GUI application for blurring faces in images and videos using deface.

This module provides a simple graphical interface for the deface library,
allowing users to select input files and output directories for face blurring.
"""
import logging
import os
import queue
import subprocess
import sys
import threading
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox
from typing import Optional, Tuple

from progress_parser import ProgressParser

try:
    import customtkinter as ctk
except ImportError:
    print(
        "Error: customtkinter is not available.\n"
        "\n"
        "Installation instructions:\n"
        "  pip install customtkinter\n"
        "\n"
        "For more information, see: https://github.com/TomSchimansky/CustomTkinter"
    )
    sys.exit(1)

# Version information
__version__ = "1.0.0"

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Set customtkinter appearance mode and color theme
ctk.set_appearance_mode("System")  # Modes: "System" (default), "Dark", "Light"
ctk.set_default_color_theme("blue")  # Themes: "blue" (default), "green", "dark-blue"


def run_deface(
    input_path: str, output_path: str, extra_args: str = ""
) -> subprocess.Popen:
    """Run the deface command as a subprocess.

    Args:
        input_path: Path to the input image or video file.
        output_path: Path where the output file should be saved.
        extra_args: Additional command-line arguments to pass to deface.

    Returns:
        A subprocess.Popen object representing the running process.

    Raises:
        FileNotFoundError: If the deface command cannot be found.
        OSError: If the subprocess cannot be started.
    """
    cmd = [
        "deface",
        input_path,
        "--output",
        output_path,
    ]
    if extra_args:
        cmd.extend(extra_args.split())

    logger.info(f"Running deface command: {' '.join(cmd)}")
    try:
        proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        return proc
    except FileNotFoundError:
        logger.error("deface command not found. Please ensure deface is installed.")
        raise
    except OSError as e:
        logger.error(f"Failed to start deface process: {e}")
        raise


def get_desktop_path() -> str:
    """Get the user's Desktop folder path.
    
    Works on Windows, macOS, and Linux. Falls back to home directory
    if Desktop folder doesn't exist.
    
    Returns:
        Path to the Desktop folder, or home directory as fallback.
    """
    desktop = Path.home() / "Desktop"
    if desktop.exists() and desktop.is_dir():
        return str(desktop)
    
    # Fallback: return home directory if Desktop doesn't exist
    # (shouldn't happen on Windows/macOS, but possible on some Linux setups)
    return str(Path.home())


def validate_paths(input_path: str, output_dir: str) -> Tuple[bool, Optional[str]]:
    """Validate input file and output directory paths.

    Args:
        input_path: Path to the input file.
        output_dir: Path to the output directory.

    Returns:
        A tuple of (is_valid, error_message). If valid, error_message is None.
    """
    if not input_path:
        return False, "Please select an input file."

    if not output_dir:
        return False, "Please select an output directory."

    input_file = Path(input_path)
    if not input_file.exists():
        return False, f"Input file does not exist: {input_path}"

    if not input_file.is_file():
        return False, f"Input path is not a file: {input_path}"

    output_path = Path(output_dir)
    if not output_path.exists():
        return False, f"Output directory does not exist: {output_dir}"

    if not output_path.is_dir():
        return False, f"Output path is not a directory: {output_dir}"

    return True, None


class DefaceApp(ctk.CTk):
    """Main application window for the Deface GUI."""

    def __init__(self):
        super().__init__()

        self.title(f"Deface — Simple v{__version__}")
        self.geometry("900x700")

        # Process tracking
        self.proc: Optional[subprocess.Popen] = None
        self.process_thread: Optional[threading.Thread] = None
        self.output_queue: queue.Queue = queue.Queue()
        self.progress_parser = ProgressParser()

        # Create UI elements
        self._create_widgets()

        # Bring window to foreground
        self._bring_to_front()

        # Schedule periodic check for process output from queue
        self._check_process_output()

    def _create_widgets(self):
        """Create and layout all GUI widgets."""
        # Main container
        main_frame = ctk.CTkFrame(self)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Title
        title_label = ctk.CTkLabel(
            main_frame, text="Face Blurring Tool", font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.pack(pady=(0, 20))

        # Input file selection
        input_frame = ctk.CTkFrame(main_frame)
        input_frame.pack(fill="x", pady=10)

        ctk.CTkLabel(input_frame, text="Input image/video:", font=ctk.CTkFont(size=14)).pack(
            anchor="w", padx=10, pady=10
        )

        input_row = ctk.CTkFrame(input_frame)
        input_row.pack(fill="x", padx=10, pady=(0, 10))

        self.input_entry = ctk.CTkEntry(input_row, placeholder_text="Select input file...")
        # Prevent entry field from triggering browse on click
        self.input_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))

        input_browse_btn = ctk.CTkButton(
            input_row, text="Browse", command=self._browse_input_file, width=100
        )
        input_browse_btn.pack(side="right")

        # Output directory selection
        output_frame = ctk.CTkFrame(main_frame)
        output_frame.pack(fill="x", pady=10)

        ctk.CTkLabel(output_frame, text="Output folder:", font=ctk.CTkFont(size=14)).pack(
            anchor="w", padx=10, pady=10
        )

        output_row = ctk.CTkFrame(output_frame)
        output_row.pack(fill="x", padx=10, pady=(0, 10))

        # Set default output folder to Desktop
        default_output = get_desktop_path()
        self.output_entry = ctk.CTkEntry(output_row, placeholder_text="Select output folder...")
        self.output_entry.insert(0, default_output)
        self.output_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))

        output_browse_btn = ctk.CTkButton(
            output_row, text="Browse", command=self._browse_output_folder, width=100
        )
        output_browse_btn.pack(side="right")

        # Progress bar section
        progress_frame = ctk.CTkFrame(main_frame)
        progress_frame.pack(fill="x", pady=10)

        self.progress_bar = ctk.CTkProgressBar(progress_frame)
        self.progress_bar.pack(fill="x", padx=10, pady=(10, 5))
        self.progress_bar.set(0)

        # Progress info labels
        progress_info_frame = ctk.CTkFrame(progress_frame)
        progress_info_frame.pack(fill="x", padx=10, pady=(0, 10))

        self.progress_info_label = ctk.CTkLabel(
            progress_info_frame,
            text="Ready",
            font=ctk.CTkFont(size=12),
        )
        self.progress_info_label.pack(side="left", padx=5)

        self.progress_stats_label = ctk.CTkLabel(
            progress_info_frame,
            text="",
            font=ctk.CTkFont(size=11),
        )
        self.progress_stats_label.pack(side="right", padx=5)

        # Log display
        log_frame = ctk.CTkFrame(main_frame)
        log_frame.pack(fill="both", expand=True, pady=10)

        ctk.CTkLabel(log_frame, text="Log:", font=ctk.CTkFont(size=14)).pack(
            anchor="w", padx=10, pady=(10, 5)
        )

        self.log_textbox = ctk.CTkTextbox(
            log_frame, font=("Courier", 11), wrap="word"
        )
        self.log_textbox.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        # Buttons
        button_frame = ctk.CTkFrame(main_frame)
        button_frame.pack(fill="x", pady=10)

        self.run_btn = ctk.CTkButton(
            button_frame, text="Run", command=self._run_deface, width=120, height=40
        )
        self.run_btn.pack(side="left", padx=10)

        quit_btn = ctk.CTkButton(
            button_frame, text="Quit", command=self._on_closing, width=120, height=40, fg_color="gray"
        )
        quit_btn.pack(side="right", padx=10)

        # Handle window close
        self.protocol("WM_DELETE_WINDOW", self._on_closing)

    def _browse_input_file(self, event=None):
        """Open file dialog to select input file.
        
        Args:
            event: Optional event parameter (for compatibility with bindings).
        """
        # Ensure we have focus before opening dialog
        self.focus()
        filename = filedialog.askopenfilename(
            parent=self,
            title="Select input image or video",
            filetypes=[
                ("All supported", "*.jpg *.jpeg *.png *.bmp *.tiff *.mp4 *.avi *.mov *.mkv"),
                ("Images", "*.jpg *.jpeg *.png *.bmp *.tiff"),
                ("Videos", "*.mp4 *.avi *.mov *.mkv"),
                ("All files", "*.*"),
            ],
        )
        if filename:
            self.input_entry.delete(0, tk.END)
            self.input_entry.insert(0, filename)

    def _browse_output_folder(self, event=None):
        """Open folder dialog to select output directory.
        
        Args:
            event: Optional event parameter (for compatibility with bindings).
        """
        # Ensure we have focus before opening dialog
        self.focus()
        folder = filedialog.askdirectory(parent=self, title="Select output folder")
        if folder:
            self.output_entry.delete(0, tk.END)
            self.output_entry.insert(0, folder)

    def _bring_to_front(self):
        """Bring the window to the foreground and give it focus."""
        # Update the window to ensure it's fully rendered
        self.update_idletasks()
        
        # On macOS, use the topmost trick to bring window to front
        if sys.platform == "darwin":
            self.attributes("-topmost", True)
            self.after(1, lambda: self.attributes("-topmost", False))
        
        # Bring window to front
        self.lift()
        
        # Force focus to the window
        self.focus_force()
        
        # On Windows, also activate the window
        if sys.platform == "win32":
            self.after(1, lambda: self.attributes("-topmost", True))
            self.after(2, lambda: self.attributes("-topmost", False))

    def _update_log(self, message: str, append: bool = False):
        """Update the log display.

        Args:
            message: The message to display.
            append: If True, append to existing log; otherwise, replace.
        """
        if append:
            self.log_textbox.insert("end", message)
        else:
            self.log_textbox.delete("1.0", tk.END)
            self.log_textbox.insert("1.0", message)
        self.log_textbox.see("end")
        logger.info(message.strip())

    def _run_deface(self):
        """Handle the Run button click."""
        if self.process_thread and self.process_thread.is_alive():
            messagebox.showwarning("Process Running", "A process is already running. Please wait for it to complete.")
            return

        input_path = self.input_entry.get().strip()
        output_dir = self.output_entry.get().strip()

        # Validate paths
        is_valid, error_msg = validate_paths(input_path, output_dir)
        if not is_valid:
            messagebox.showerror("Error", error_msg or "Invalid input or output path.")
            self._update_log(f"Error: {error_msg}\n")
            return

        # Construct output path with _blurred suffix
        try:
            input_filename = os.path.basename(input_path)
            name, ext = os.path.splitext(input_filename)
            output_filename = f"{name}_blurred{ext}"
            out_path = os.path.join(output_dir, output_filename)
            self._update_log(f"Processing: {input_path}\n")
            self._update_log(f"Output: {out_path}\n", append=True)

            # Disable run button and reset progress
            self.run_btn.configure(state="disabled")
            self.progress_bar.set(0)
            self.progress_info_label.configure(text="Starting...")
            self.progress_stats_label.configure(text="")

            # Start deface process in background thread
            self.process_thread = threading.Thread(
                target=self._run_deface_thread,
                args=(input_path, out_path),
                daemon=True
            )
            self.process_thread.start()
            self._update_log("Started processing...\n", append=True)
        except Exception as e:
            error_msg = f"Failed to start deface: {str(e)}"
            logger.error(error_msg)
            messagebox.showerror("Error", error_msg)
            self._update_log(f"Error: {error_msg}\n", append=True)
            self.proc = None
            self.run_btn.configure(state="normal")

    def _read_stream(self, stream, stream_type: str):
        """Read from a stream (stdout or stderr) and queue output."""
        try:
            for line in iter(stream.readline, ''):
                if line:
                    self.output_queue.put((stream_type, line))
        except Exception as e:
            logger.error(f"Error reading {stream_type}: {e}")
        finally:
            stream.close()

    def _run_deface_thread(self, input_path: str, output_path: str):
        """Run deface in a background thread and queue output for UI updates."""
        try:
            # Start the subprocess
            self.proc = run_deface(input_path, output_path)
            
            # Start threads to read stdout and stderr concurrently
            stdout_thread = threading.Thread(
                target=self._read_stream,
                args=(self.proc.stdout, 'stdout'),
                daemon=True
            )
            stderr_thread = threading.Thread(
                target=self._read_stream,
                args=(self.proc.stderr, 'stderr'),
                daemon=True
            )
            
            stdout_thread.start()
            stderr_thread.start()
            
            # Wait for process to complete
            return_code = self.proc.wait()
            
            # Wait for both reading threads to finish
            stdout_thread.join(timeout=1)
            stderr_thread.join(timeout=1)
            
            # Queue completion message
            self.output_queue.put(('done', return_code))
            
        except Exception as e:
            logger.error(f"Error in deface thread: {e}")
            self.output_queue.put(('error', str(e)))
        finally:
            self.proc = None

    def _check_process_output(self):
        """Periodically check for process output from queue and update UI."""
        try:
            # Process all available messages from the queue
            while True:
                try:
                    msg_type, content = self.output_queue.get_nowait()
                    
                    if msg_type == 'stdout':
                        self._update_log(content, append=True)
                        # Try to parse progress from stdout
                        self._update_progress(content)
                    elif msg_type == 'stderr':
                        # Display stderr output (may include warnings, progress, or errors)
                        self._update_log(content, append=True)
                        # Try to parse progress from stderr (tqdm often outputs to stderr)
                        self._update_progress(content)
                    elif msg_type == 'done':
                        return_code = content
                        # Complete the progress bar
                        self.progress_bar.set(1.0)
                        if return_code == 0:
                            self._update_log("\n✓ Process completed successfully.\n", append=True)
                            self.progress_info_label.configure(text="✓ Completed")
                        else:
                            self._update_log(
                                f"\n✗ Process finished with error code: {return_code}\n", append=True
                            )
                            self.progress_info_label.configure(text="✗ Failed")
                        self.progress_stats_label.configure(text="")
                        self.proc = None
                        self.process_thread = None
                        self.run_btn.configure(state="normal")
                    elif msg_type == 'error':
                        error_msg = f"Error: {content}\n"
                        self._update_log(error_msg, append=True)
                        self.progress_bar.set(0)
                        self.progress_info_label.configure(text="Error")
                        self.progress_stats_label.configure(text="")
                        self.proc = None
                        self.process_thread = None
                        self.run_btn.configure(state="normal")
                        
                except queue.Empty:
                    break
        except Exception as e:
            logger.error(f"Error processing output queue: {e}")
            self._update_log(f"\nError processing output: {str(e)}\n", append=True)
            self.proc = None
            self.process_thread = None
            self.run_btn.configure(state="normal")

        # Schedule next check
        self.after(50, self._check_process_output)

    def _update_progress(self, line: str):
        """Update progress bar and info labels from a line of output.
        
        Args:
            line: A line of output that may contain progress information.
        """
        if self.progress_parser.parse(line):
            # Update progress bar
            progress_fraction = self.progress_parser.get_progress_fraction()
            self.progress_bar.set(progress_fraction)
            
            # Update info label with percentage and current/total
            info_text = f"{self.progress_parser.percentage:.0f}% ({self.progress_parser.current}/{self.progress_parser.total})"
            self.progress_info_label.configure(text=info_text)
            
            # Update stats label with ETA, elapsed, and rate
            stats_text = f"ETA: {self.progress_parser.format_eta()} | Elapsed: {self.progress_parser.format_elapsed()} | {self.progress_parser.format_rate()}"
            self.progress_stats_label.configure(text=stats_text)

    def _on_closing(self):
        """Handle window closing event."""
        if self.process_thread and self.process_thread.is_alive():
            if messagebox.askokcancel("Quit", "A process is running. Do you want to terminate it and quit?"):
                logger.info("Terminating running process...")
                if self.proc and self.proc.poll() is None:
                    self.proc.terminate()
                    try:
                        self.proc.wait(timeout=5)
                    except subprocess.TimeoutExpired:
                        self.proc.kill()
                # Wait for thread to finish
                self.process_thread.join(timeout=1)
                self.destroy()
        else:
            self.destroy()


def main() -> None:
    """Main application entry point."""
    app = DefaceApp()
    try:
        app.mainloop()
    except KeyboardInterrupt:
        logger.info("Application interrupted by user")
        if app.process_thread and app.process_thread.is_alive():
            if app.proc and app.proc.poll() is None:
                app.proc.terminate()
    except Exception as e:
        logger.exception("Unexpected error in main loop")
        messagebox.showerror("Error", f"An unexpected error occurred: {str(e)}")
    finally:
        logger.info("Application closed")


if __name__ == "__main__":
    main()
