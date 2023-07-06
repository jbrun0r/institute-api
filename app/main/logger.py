import yaml
from .config import app_config

def get_logging_config():
    """Get the logging configuration dictionary."""
    with open('logging_config.yaml', 'r') as config_file:
        logging_config = yaml.safe_load(config_file)
    
    log_level = app_config.LOG_LEVEL
    logging_config['root']['level'] = log_level

    return logging_config
