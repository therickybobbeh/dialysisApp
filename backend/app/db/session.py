from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import time
import logging
from sqlalchemy.exc import SQLAlchemyError, OperationalError
from tenacity import retry, stop_after_attempt, wait_exponential

from app.core.config import settings
from app.db.base_class import Base

logger = logging.getLogger(__name__)

# Azure PostgreSQL connection configuration with optimized settings
engine_config = {
    'pool_size': settings.DB_POOL_SIZE,         # Connection pool size
    'max_overflow': settings.DB_MAX_OVERFLOW,   # Max connections above pool size
    'pool_timeout': settings.DB_POOL_TIMEOUT,   # Seconds to wait for pool connection
    'pool_recycle': settings.DB_POOL_RECYCLE,   # Recycle connections after this many seconds
    'connect_args': {
        'connect_timeout': 10,                  # Connection timeout in seconds
        'application_name': 'pd_management_app' # Identify application in Azure monitoring
    }
}

# Create database engine with retry logic for connection establishment
@retry(
    stop=stop_after_attempt(settings.DB_MAX_RETRIES),
    wait=wait_exponential(multiplier=1, min=1, max=10),
    reraise=True
)
def get_engine():
    """Create SQLAlchemy engine with retry logic for connection resilience"""
    try:
        if settings.USE_MANAGED_IDENTITY and settings.AZURE_DEPLOYMENT:
            # For Azure deployment with Managed Identity
            from azure.identity import DefaultAzureCredential
            token_credential = DefaultAzureCredential()
            
            # Get access token for PostgreSQL
            # Note: This is a simplified example - production code might need
            # to include the specific PostgreSQL resource URL
            access_token = token_credential.get_token("https://ossrdbms-aad.database.windows.net/.default")
            
            # Update connection args with access token
            engine_config['connect_args']['password'] = access_token.token
        
        logger.info(f"Creating database engine with pool size: {settings.DB_POOL_SIZE}")
        return create_engine(settings.DATABASE_URL, **engine_config)
    except Exception as e:
        logger.error(f"Error creating database engine: {str(e)}")
        raise

# Initialize the engine
try:
    engine = get_engine()
    logger.info("Database engine successfully created")
except Exception as e:
    logger.critical(f"Failed to create database engine after multiple attempts: {str(e)}")
    # In production, you might want to have a fallback or alert system here
    raise

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    """Get database session with retry logic for transient errors"""
    db = SessionLocal()
    try:
        # Verify connection is working
        db.execute("SELECT 1")
        yield db
    except OperationalError as e:
        logger.warning(f"Database operational error encountered: {e}")
        # Retry logic could be implemented here if needed
        raise
    except SQLAlchemyError as e:
        logger.error(f"Database error: {e}")
        raise
    finally:
        db.close()
