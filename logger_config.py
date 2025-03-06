import logging
import os
from utils import get_exe_directory

def setup_logger():
    """Configure logging for the application"""
    # Get log file path in executable directory
    log_path = os.path.join(get_exe_directory(), 'output.log')
    
    # Create logger
    logger = logging.getLogger('ImportExportChecker')
    logger.setLevel(logging.DEBUG)  # Capture all levels
    
    # Create file handler with DEBUG level to capture everything
    file_handler = logging.FileHandler(log_path, mode='w', encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)  # Changed to DEBUG to capture all logs
    
    # Create console handler (won't be visible in exe but useful during development)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    
    # Create formatter with more detailed information
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Add formatter to handlers
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    # Add handlers to logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

# Create and configure logger
logger = setup_logger() 