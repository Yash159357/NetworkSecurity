import logging
import sys
import os
import datetime

class ColorFormatter(logging.Formatter):
    green = "\033[92m"
    yellow = "\033[93m"
    red = "\033[91m"
    bold_red = "\033[31m"
    reset = "\033[0m"

    def __init__(self, fmt=None, datefmt=None):
        super().__init__(fmt, datefmt)
        self.FORMATS = {
            logging.DEBUG: self.green + self._fmt + self.reset,
            logging.INFO: self.green + self._fmt + self.reset,
            logging.WARNING: self.yellow + self._fmt + self.reset,
            logging.ERROR: self.red + self._fmt + self.reset,
            logging.CRITICAL: self.bold_red + self._fmt + self.reset
        }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt, datefmt=self.datefmt)
        return formatter.format(record)

# Log file setup
LOG_FILE = f"{datetime.datetime.now().strftime('%Y_%m_%d___%H_%M_%S')}.log"
log_path = os.path.join(os.getcwd(), "logs")
os.makedirs(log_path, exist_ok=True)

log_format = '[%(asctime)s] - %(lineno)d - %(name)s - %(levelname)s - %(message)s'
date_format = '%Y-%m-%d %H:%M:%S'

# Console Logging
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(ColorFormatter(log_format, date_format))
# Configure logging
logging.basicConfig(
    level = logging.INFO,
    format = log_format,
    datefmt = date_format,
    handlers = [
        logging.FileHandler(os.path.join(log_path, LOG_FILE)),
        console_handler
    ]
)

logger = logging.getLogger()
