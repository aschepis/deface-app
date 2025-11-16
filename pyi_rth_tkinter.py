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
        # On macOS, Tcl/Tk libraries are in Contents/lib/tcl8.6 and Contents/lib/tk8.6
        # This is where Tcl expects to find init.tcl
        contents_dir = meipass.parent
        tcl_path = contents_dir / 'lib' / 'tcl8.6'
        tk_path = contents_dir / 'lib' / 'tk8.6'

        # Fallback to Resources if not found in lib (for backward compatibility)
        if not tcl_path.exists():
            resources_dir = contents_dir / 'Resources'
            tcl_path = resources_dir / 'tcl'
        if not tk_path.exists():
            resources_dir = contents_dir / 'Resources'
            tk_path = resources_dir / 'tk'
    else:
        # Standard PyInstaller layout (Windows/Linux)
        tcl_path = meipass / 'tcl'
        tk_path = meipass / 'tk'

    if tcl_path.exists():
        os.environ['TCL_LIBRARY'] = str(tcl_path)
    if tk_path.exists():
        os.environ['TK_LIBRARY'] = str(tk_path)
