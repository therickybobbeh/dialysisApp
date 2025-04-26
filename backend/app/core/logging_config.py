import logging
import json
import os
import sys
from logging.handlers import TimedRotatingFileHandler
import uuid
from datetime import datetime
from app.core.config import settings
from app.core.azure_integration import setup_azure_log_handler

# Generate a unique request ID for correlation
def get_request_id():
    return str(uuid.uuid4())

# Custom JSON formatter for structured logging
class JsonFormatter(logging.Formatter):
    def format(self, record):
        log_record = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        # Add exception info if present
        if record.exc_info:
            log_record["exception"] = self.formatException(record.exc_info)
        
        # Add custom fields if available
        if hasattr(record, "request_id"):
            log_record["request_id"] = record.request_id
        if hasattr(record, "user_id"):
            log_record["user_id"] = record.user_id
        if hasattr(record, "correlation_id"):
            log_record["correlation_id"] = record.correlation_id
            
        return json.dumps(log_record)

# Standard formatter for readability in development
class StandardFormatter(logging.Formatter):
    def format(self, record):
        if hasattr(record, "request_id"):
            return f"{datetime.utcnow().isoformat()} - {record.levelname} - [ReqID:{record.request_id}] - {record.getMessage()}"
        return f"{datetime.utcnow().isoformat()} - {record.levelname} - {record.getMessage()}"

def setup_logging():
    """Configure application logging with file rotation, console output,
    and optional Application Insights integration"""
    
    # Create logs directory if it doesn't exist
    if not os.path.exists("logs"):
        os.makedirs("logs")
    
    # Root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, settings.LOG_LEVEL))
    
    # Remove existing handlers to avoid duplicates on reload
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # File handler with rotation
    file_handler = TimedRotatingFileHandler(
        os.path.join("logs", settings.LOG_FILE),
        when="midnight",
        interval=1,
        backupCount=settings.LOG_BACKUP_COUNT
    )
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    
    # Configure formatters based on settings
    if settings.STRUCTURED_LOGGING:
        file_formatter = JsonFormatter()
    else:
        file_formatter = StandardFormatter()
    
    # Always use standard formatter for console for readability
    console_formatter = StandardFormatter()
    
    # Apply formatters
    file_handler.setFormatter(file_formatter)
    console_handler.setFormatter(console_formatter)
    
    # Add handlers to root logger
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)
    
    # Set up Azure Application Insights logging if enabled
    if settings.AZURE_DEPLOYMENT and settings.ENABLE_APP_INSIGHTS:
        azure_handler = setup_azure_log_handler()
        if azure_handler:
            # Use JSON formatter for Azure logs
            azure_handler.setFormatter(JsonFormatter())
            root_logger.addHandler(azure_handler)
            logging.info("Azure Application Insights logging enabled")
    
    # Return a logger instance for this module
    return logging.getLogger(__name__)

# Initialize logger
logger = setup_logging()
