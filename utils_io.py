"""Utility functions for file operations and safe I/O handling."""

import threading

class ThreadSafeWriter:
    """
    Thread-safe file writer that keeps the file open for efficient writing.
    """
    def __init__(self, filename, encoding="utf-8"):
        self.filename = filename
        self.encoding = encoding
        self.file = None
        self.lock = threading.Lock()

    def __enter__(self):
        self.file = open(self.filename, "a", encoding=self.encoding)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.file:
            self.file.close()

    def write(self, content):
        """Thread-safe write method."""
        with self.lock:
            if self.file:
                self.file.write(f"{content}\n")
                self.file.flush()

def stream_file_lines(filename, encoding="utf-8"):
    """
    Generator that yields stripped lines from a file.

    Args:
        filename (str): Path to the file to read.
        encoding (str, optional): File encoding. Defaults to "utf-8".
    
    Returns:
        generator: Generator yielding stripped lines from the file.
    """
    try:
        with open(filename, "r", encoding=encoding, errors="replace") as f:
            for line in f:
                try:
                    clean_line = line.strip()
                    if clean_line:
                        yield clean_line
                except Exception:
                    # Skip malformed lines
                    continue
    except Exception as e:
        # Re-raise major errors (file not found, etc.) for the engine to catch
        raise e
