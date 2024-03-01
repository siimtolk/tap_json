
import os
LOG_DIR = ".meltano/logs/tap_json/"
PROCESSED_FILES_LOG_PATH = "processed_files.log"

def log_processed_file_path(file_path):
        """Appends the processed file path to the log file."""

         # Check if the target folder exists, create it if it does not
        if not os.path.exists(LOG_DIR):
            os.makedirs(LOG_DIR)

        with open( os.path.join(LOG_DIR,PROCESSED_FILES_LOG_PATH) , "a") as file:
            file.write(file_path + "\n")

def is_file_processed(file_path):
        """Checks if the given file path is in the processed files log."""
        try:
            with open(os.path.join(LOG_DIR,PROCESSED_FILES_LOG_PATH) , "r") as file:
                for line in file:
                    if line.strip() == file_path:
                        return True
        except FileNotFoundError:
            # Log file doesn't exist means no file has been processed yet
            return False
        return False
