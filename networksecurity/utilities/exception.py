from networksecurity.utilities.logger import logger
import sys

class NetworkSecurityException(Exception):
    def __init__(self, message, error_detail: sys, is_critical: bool = False):
        _, _, exc_tb = error_detail.exc_info()
        self.lineno = exc_tb.tb_lineno
        self.filename = exc_tb.tb_frame.f_code.co_filename
        self.error_message = f"Error occurred in script: {self.filename} at line: {self.lineno} error message: {message}"

        if is_critical:
            logger.critical(self.error_message)
        else:
            logger.error(self.error_message)

        super().__init__(message)

    def __str__(self):
        return self.args[0]