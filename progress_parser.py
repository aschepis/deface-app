"""Progress parser for tqdm-style progress output."""
import logging
import re
from typing import Optional

logger = logging.getLogger(__name__)


class ProgressParser:
    """Parse tqdm-style progress output and extract progress information.
    
    Parses lines like: "33%|███▎      | 415/1275 [00:13<00:27, 31.12it/s]"
    """
    
    # Regex pattern to match tqdm progress bar format
    # Format: percentage%|bar|current/total [elapsed<remaining, rate]
    PROGRESS_PATTERN = re.compile(
        r'(\d+)%\s*\|.*?\|\s*(\d+)/(\d+)\s*\[(\d+):(\d+)<(\d+):(\d+),\s*([\d.]+)(\w+)/s\]'
    )
    
    def __init__(self):
        self.percentage = 0.0
        self.current = 0
        self.total = 0
        self.elapsed_seconds = 0
        self.remaining_seconds = 0
        self.rate = 0.0
        self.rate_unit = ""
        self.is_valid = False
    
    def parse(self, line: str) -> bool:
        """Parse a progress line and extract information.
        
        Args:
            line: A line of output that may contain tqdm progress information.
            
        Returns:
            True if progress information was found and parsed, False otherwise.
        """
        match = self.PROGRESS_PATTERN.search(line)
        if not match:
            self.is_valid = False
            return False
        
        try:
            self.percentage = float(match.group(1))
            self.current = int(match.group(2))
            self.total = int(match.group(3))
            elapsed_minutes = int(match.group(4))
            elapsed_secs = int(match.group(5))
            remaining_minutes = int(match.group(6))
            remaining_secs = int(match.group(7))
            self.rate = float(match.group(8))
            self.rate_unit = match.group(9)
            
            self.elapsed_seconds = elapsed_minutes * 60 + elapsed_secs
            self.remaining_seconds = remaining_minutes * 60 + remaining_secs
            
            self.is_valid = True
            return True
        except (ValueError, IndexError) as e:
            logger.debug(f"Error parsing progress line: {e}")
            self.is_valid = False
            return False
    
    def format_eta(self) -> str:
        """Format estimated time remaining as a human-readable string.
        
        Returns:
            Formatted ETA string (e.g., "00:27", "1:23", "2h 15m").
        """
        if not self.is_valid or self.remaining_seconds <= 0:
            return "--:--"
        
        if self.remaining_seconds < 3600:
            # Less than an hour: show as MM:SS
            minutes = self.remaining_seconds // 60
            seconds = self.remaining_seconds % 60
            return f"{minutes:02d}:{seconds:02d}"
        else:
            # More than an hour: show as Xh Ym
            hours = self.remaining_seconds // 3600
            minutes = (self.remaining_seconds % 3600) // 60
            return f"{hours}h {minutes}m"
    
    def format_elapsed(self) -> str:
        """Format elapsed time as a human-readable string.
        
        Returns:
            Formatted elapsed time string (e.g., "00:13", "1:23").
        """
        if not self.is_valid:
            return "00:00"
        
        minutes = self.elapsed_seconds // 60
        seconds = self.elapsed_seconds % 60
        return f"{minutes:02d}:{seconds:02d}"
    
    def format_rate(self) -> str:
        """Format processing rate as a human-readable string.
        
        Returns:
            Formatted rate string (e.g., "31.12 it/s").
        """
        if not self.is_valid or self.rate <= 0:
            return "0 it/s"
        
        return f"{self.rate:.2f} {self.rate_unit}/s"
    
    def get_progress_fraction(self) -> float:
        """Get progress as a fraction between 0.0 and 1.0.
        
        Returns:
            Progress fraction (0.0 to 1.0).
        """
        if not self.is_valid or self.total == 0:
            return 0.0
        return min(1.0, max(0.0, self.current / self.total))

