"""Home view for the Sightline application.

The home view is the default view that is shown when the application is launched.
"""

import logging
import tkinter.messagebox as messagebox

import customtkinter as ctk
from typing import Any
from views.base_view import BaseView

logger = logging.getLogger(__name__)


class HomeView(BaseView):
    """Home view for the Sightline application."""

    def __init__(self, parent: ctk.CTk, app: Any):
        super().__init__(parent, app)
        self.create_widgets()

    def create_widgets(self):
        """Create and layout all GUI widgets."""
        # Main container with rounded border appearance
        main_frame = ctk.CTkFrame(self, corner_radius=15)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Title section
        title_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        title_frame.pack(pady=(30, 10))

        # Title "Sightline"
        title_label = ctk.CTkLabel(
            title_frame,
            text="Sightline",
            font=ctk.CTkFont(size=36, weight="bold"),
        )
        title_label.pack()

        # Double underline effect (using two separator lines)
        underline1 = ctk.CTkFrame(
            title_frame, height=2, fg_color=("gray70", "gray30")
        )
        underline1.pack(fill="x", padx=50, pady=(5, 0))
        underline2 = ctk.CTkFrame(
            title_frame, height=2, fg_color=("gray70", "gray30")
        )
        underline2.pack(fill="x", padx=50, pady=(2, 0))

        # "Choose a Task" heading
        task_heading = ctk.CTkLabel(
            main_frame,
            text="Choose a Task",
            font=ctk.CTkFont(size=24, weight="normal"),
        )
        task_heading.pack(pady=(40, 30))

        # Task buttons container
        buttons_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        buttons_frame.pack(pady=20, padx=40, fill="both", expand=True)

        # Three task buttons in a row
        button_width = 200
        button_height = 120

        # Deface button
        deface_button = ctk.CTkButton(
            buttons_frame,
            text="Deface\n(Automatic Face Blur)",
            font=ctk.CTkFont(size=16, weight="bold"),
            width=button_width,
            height=button_height,
            corner_radius=15,
            command=self._on_deface_clicked,
        )
        deface_button.pack(side="left", padx=15, expand=True, fill="both")

        # Smudge button
        smudge_button = ctk.CTkButton(
            buttons_frame,
            text="Smudge\n(Manual Face Blur)",
            font=ctk.CTkFont(size=16, weight="bold"),
            width=button_width,
            height=button_height,
            corner_radius=15,
            command=self._on_smudge_clicked,
        )
        smudge_button.pack(side="left", padx=15, expand=True, fill="both")

        # Transcribe button
        transcribe_button = ctk.CTkButton(
            buttons_frame,
            text="Transcribe",
            font=ctk.CTkFont(size=16, weight="bold"),
            width=button_width,
            height=button_height,
            corner_radius=15,
            command=self._on_transcribe_clicked,
        )
        transcribe_button.pack(side="left", padx=15, expand=True, fill="both")

        # Settings button in bottom-left
        settings_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        settings_frame.pack(side="bottom", anchor="w", padx=20, pady=20, fill="x")

        settings_button = ctk.CTkButton(
            settings_frame,
            text="Settings",
            font=ctk.CTkFont(size=14),
            width=120,
            height=35,
            corner_radius=10,
            command=self._on_settings_clicked,
        )
        settings_button.pack(side="left")

    def _on_deface_clicked(self):
        """Handle Deface button click - navigate to batch processing view."""
        if hasattr(self.app, "show_view"):
            self.app.show_view("batch_processing")

    def _on_smudge_clicked(self):
        """Handle Smudge button click - open Face Smudge window."""
        if hasattr(self.app, "_open_face_smudge"):
            self.app._open_face_smudge()
        elif hasattr(self.app, "open_face_smudge"):
            self.app.open_face_smudge()

    def _on_transcribe_clicked(self):
        """Handle Transcribe button click."""
        # TODO: Implement transcribe functionality
        # For now, show a placeholder message
        messagebox.showinfo("Transcribe", "Transcribe feature coming soon!")

    def _on_settings_clicked(self):
        """Handle Settings button click - open settings dialog."""
        try:
            from dialogs import ConfigDialog
            dialog = ConfigDialog(self.app, self.app.config)
            self.app.wait_window(dialog)

            if dialog.result is not None:
                self.app.config = dialog.result
                if hasattr(self.app, "_save_config"):
                    self.app._save_config()
        except Exception as e:
            logger.error(f"Error opening settings dialog: {e}")
            messagebox.showerror("Error", f"Could not open settings:\n{str(e)}")
