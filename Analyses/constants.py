STORAGE_DIR = None

def set_storage_dir(storage_dir: str) -> None:
    """Set the storage directory for the analysis results."""
    global STORAGE_DIR
    STORAGE_DIR = storage_dir

def get_storage_dir() -> str:
    """Get the storage directory for the analysis results."""
    if STORAGE_DIR is None:
        raise ValueError("Storage directory not set. Please set it using set_storage_dir().")
    return STORAGE_DIR