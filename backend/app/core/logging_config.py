import logging
from logging.handlers import TimedRotatingFileHandler
import os

LOG_FILE = "app.log"  #  Ensure the log file is defined
LOG_BACKUP_COUNT = 5   #  Prevents excessive log files

#  Ensure directory exists
if not os.path.exists("logs"):
    os.makedirs("logs")

log_handler = TimedRotatingFileHandler(
    os.path.join("logs", LOG_FILE),
    when="midnight",
    interval=1,
    backupCount=LOG_BACKUP_COUNT
)
log_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
log_handler.suffix = "%Y-%m-%d"

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.addHandler(log_handler)
