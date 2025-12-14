"""PyInstaller runtime hook for tqdm library.

This hook patches tqdm.contrib.concurrent.ensure_lock to handle the 'disabled_tqdm'
class that huggingface_hub uses. In frozen applications, this class causes an
AttributeError because it lacks the expected _lock attribute handling.
"""

import sys

# Apply patch both in PyInstaller bundles and regular Python environments
# The disabled_tqdm issue can occur in both contexts
if True:  # Always apply the patch
    try:
        # Import the module to patch
        import tqdm.contrib.concurrent
        import threading
        from contextlib import contextmanager

        # Debug output to verify hook execution
        # print("DEBUG: PyInstaller runtime hook for tqdm starting...", file=sys.stderr)

        _orig_ensure_lock = tqdm.contrib.concurrent.ensure_lock

        @contextmanager
        def _patched_ensure_lock(tqdm_class, lock_name=""):
            """
            Patched ensure_lock that handles the 'disabled_tqdm' class.

            When huggingface_hub disables progress bars (often in frozen apps),
            it uses a disabled_tqdm class that causes crashes in ensure_lock
            because it doesn't support the lock attribute operations.
            """
            # Handle the special disabled_tqdm class by name
            class_name = getattr(tqdm_class, "__name__", "")
            if class_name == "disabled_tqdm":
                # For disabled_tqdm, create a fresh lock and yield it.
                # We don't try to manage the lock on tqdm_class since
                # disabled_tqdm doesn't support lock operations.
                lock = threading.Lock()
                yield lock
                return

            # Try to call the original function, but catch AttributeError
            # in case it still fails (defensive programming)
            try:
                # The original ensure_lock is a context manager, so we delegate to it
                with _orig_ensure_lock(tqdm_class, lock_name) as lock:
                    yield lock
            except (AttributeError, TypeError) as e:
                # If the original function fails (likely _lock missing or wrong type),
                # yield a fresh lock as fallback
                error_str = str(e)
                if lock_name in error_str or "_lock" in error_str or "context manager" in error_str.lower():
                    # Create a fresh lock and yield it
                    # We don't manage it on tqdm_class since the class doesn't support it
                    lock = threading.Lock()
                    yield lock
                else:
                    # Re-raise if it's a different error
                    raise

        tqdm.contrib.concurrent.ensure_lock = _patched_ensure_lock
        # print("DEBUG: Successfully patched tqdm.contrib.concurrent.ensure_lock", file=sys.stderr)

    except ImportError:
        # tqdm might not be present or used, which is fine
        pass
    except Exception as e:
        print(f"Warning: Failed to patch tqdm runtime hook: {e}", file=sys.stderr)
