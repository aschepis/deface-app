"""PyInstaller runtime hook for tkinter/Tcl initialization.

This hook ensures that Tcl/Tk can find its initialization files when
the application is bundled with PyInstaller.
"""

import os
import sys
from pathlib import Path

# Set TCL/TK library paths for bundled application
if hasattr(sys, '_MEIPASS'):
    # Running in PyInstaller bundle
    # For macOS .app bundles, _MEIPASS points to Contents/MacOS/
    # but PyInstaller puts data files in Contents/Resources/
    meipass = Path(sys._MEIPASS)

    # Check if we're in a .app bundle (macOS)
    if sys.platform == 'darwin' and 'Contents/MacOS' in str(meipass):
        # Go up to Contents, then into Resources
        resources_dir = meipass.parent / 'Resources'
        tcl_path = resources_dir / 'tcl'
        tk_path = resources_dir / 'tk'
    else:
        # Standard PyInstaller layout (Windows/Linux)
        tcl_path = meipass / 'tcl'
        tk_path = meipass / 'tk'

    if tcl_path.exists():
        os.environ['TCL_LIBRARY'] = str(tcl_path)
    if tk_path.exists():
        os.environ['TK_LIBRARY'] = str(tk_path)
