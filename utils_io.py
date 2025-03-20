"""Utility functions for file operations and safe I/O handling."""

def safe_write_to_file(filename, content):
    """
    Safely write content to a file using proper resource management.
    
    Args:
        filename (str): The file to write to
        content (str): Content to be written
    
    Returns:
        bool: True if writing was successful, False otherwise
    """
    try:
        with open(filename, "a") as f:
            f.write(f"{content}\n")
        return True
    except Exception as e:
        print(f"Error writing to file {filename}: {e}")
        return False

def safe_read_from_file(filename, encoding="Latin-1"):
    """
    Safely read content from a file using proper resource management.
    
    Args:
        filename (str): The file to read from
        encoding (str): File encoding (default: Latin-1)
        
    Returns:
        list: Lines from the file or empty list if file cannot be read
    """
    try:
        with open(filename, "r", encoding=encoding) as f:
            return f.read().splitlines()
    except Exception as e:
        print(f"Error reading file {filename}: {e}")
        return []
