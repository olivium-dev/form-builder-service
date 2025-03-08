import json
import logging

logger = logging.getLogger(__name__)

def load_config(file_path: str):
    """
    Load a JSON configuration file and return its data.
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            config_data = json.load(f)
            logger.info(f"Loaded configuration from {file_path}")
            return config_data
    except Exception as e:
        logger.error(f"Error loading config file {file_path}: {e}")
        raise RuntimeError(f"Error loading config file {file_path}: {e}") 