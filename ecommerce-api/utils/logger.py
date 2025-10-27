import logging
import os
from logging.handlers import RotatingFileHandler

def setup_logger(name,log_file=None,level=logging.INFO):
    logger = logging.getLogger(name)
    logger.setLevel(level=level)
    logger.propagate = False 
    if not logger.hasHandlers():
        console_handler = logging.StreamHandler()
        format = logging.Formatter('[%(asctime)s] %(levelname)s: %(message)s')
        console_handler.setFormatter(format)
        logger.addHandler(console_handler)
        if log_file:
            log_dir = os.path.dirname(log_file)
            if log_dir and not os.path.exists(log_dir):
                os.makedirs(log_dir)
            file_handler = RotatingFileHandler(log_file,maxBytes=10*1024*1024,backupCount=5)
            file_handler.setFormatter(format)
            logger.addHandler(file_handler)
    return logger 

def get_app_logger():
    return setup_logger('ecommerce_api',log_file='logs/app.log',level=logging.DEBUG)
def get_request_logger():
    return setup_logger('ecommerce_api.requests',log_file='logs/requests.log',level=logging.INFO)

def get_error_logger():
    return setup_logger('ecommerce_api.errors',log_file='logs/errors.log',level=logging.ERROR)

