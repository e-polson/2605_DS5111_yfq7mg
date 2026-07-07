"""
This module cleans up string IDs from standard input
"""

import os
import re
import sys
import logging

# Set up absolute pathing to ensure logs land cleanly in the /logs directory
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
LOG_DIR = os.path.join(BASE_DIR, "logs")

# Create the logs directory if it doesn't exist yet
os.makedirs(LOG_DIR, exist_ok=True)

# Configure logging to point directly into logs/pipeline_autid.log
logging.basicConfig(
    filename=os.path.join(LOG_DIR, "pipeline_autid.log"),
    encoding="utf-8",
    filemode="w",
    level=logging.INFO,
    format="%(message)s",
)

log_file = logging.getLogger(__name__)

log_file = logging.getLogger(__name__)


def check_id(id_str):
    """Confirms whether a string is a valid ID"""
    cleaned_id = id_str.strip()

    if re.match(r"[A-Za-z0-9_0]{11}$", cleaned_id):
        print(cleaned_id)
    else:
        log_file.info(cleaned_id)


def main():
    """Main execution function"""
    if sys.stdin.isatty():
        while True:
            try:
                current_id = input()
                check_id(current_id)
            except (KeyboardInterrupt, EOFError):
                sys.exit(0)
    else:
        try:
            for current_id in sys.stdin:
                check_id(current_id)
        except KeyboardInterrupt:
            sys.exit(0)


if __name__ == "__main__":
    main()
