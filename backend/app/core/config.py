from pydantic_settings import BaseSettings
import os

class Settings(BaseSettings):
    # Azure Deployment Configuration
    AZURE_DEPLOYMENT: bool = os.getenv("AZURE_DEPLOYMENT", "false").lower() == "true"
    
    # Database Configuration
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://postgres:admin@localhost/pd_management")
    
    # Azure PostgreSQL Connection Pool Settings
    DB_POOL_SIZE: int = int(os.getenv("DB_POOL_SIZE", 20))
    DB_MAX_OVERFLOW: int = int(os.getenv("DB_MAX_OVERFLOW", 10))
    DB_POOL_TIMEOUT: int = int(os.getenv("DB_POOL_TIMEOUT", 30))
    DB_POOL_RECYCLE: int = int(os.getenv("DB_POOL_RECYCLE", 1800))  # Recycle connections after 30 minutes
    DB_MAX_RETRIES: int = int(os.getenv("DB_MAX_RETRIES", 5))
    
    # Azure Authentication Settings
    USE_MANAGED_IDENTITY: bool = os.getenv("USE_MANAGED_IDENTITY", "false").lower() == "true"
    AZURE_TENANT_ID: str = os.getenv("AZURE_TENANT_ID", "")
    
    # Application Insights Integration
    APPLICATION_INSIGHTS_CONNECTION_STRING: str = os.getenv("APPLICATIONINSIGHTS_CONNECTION_STRING", "")
    ENABLE_APP_INSIGHTS: bool = os.getenv("ENABLE_APP_INSIGHTS", "false").lower() == "true"
    
    # Authentication & Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your_secret_key")
    REFRESH_SECRET_KEY: str = os.getenv("REFRESH_SECRET_KEY", "your_refresh_secret_key")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 120))
    KEY_VAULT_NAME: str = os.getenv("KEY_VAULT_NAME", "")  # Azure Key Vault for secrets management

    # Logging Configuration
    LOG_FILE: str = os.getenv("LOG_FILE", "app.log")
    LOG_BACKUP_COUNT: int = int(os.getenv("LOG_BACKUP_COUNT", 5))
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    STRUCTURED_LOGGING: bool = os.getenv("STRUCTURED_LOGGING", "true").lower() == "true"

    # Risk Analysis Settings
    RISK_THRESHOLD: float = float(os.getenv("RISK_THRESHOLD", 1.0))

    # Seeding Configuration
    RUN_SEEDER: bool = os.getenv("RUN_SEEDER", "true").lower() == "true"

    # HAPI FHIR Server Base url
    HAPI_FHIR_BASE_URL: str = os.getenv("HAPI_BASE_URL", "http://hapi:8080/fhir/")
    
    # Health Check Settings
    HEALTH_CHECK_INCLUDE_DB: bool = os.getenv("HEALTH_CHECK_INCLUDE_DB", "true").lower() == "true"

    class Config:
        env_file = ".env"

    @property
    def get_db_connection_string(self):
        """
        Dynamically constructs database connection string based on environment
        Useful when switching between local development and Azure deployment
        """
        if self.AZURE_DEPLOYMENT:
            # Extract components from the DATABASE_URL for Azure format
            # Azure PostgreSQL connection format differs from standard
            host = os.getenv("POSTGRES_HOST", "")
            user = os.getenv("POSTGRES_USER", "")
            dbname = os.getenv("POSTGRES_DB", "")
            port = os.getenv("POSTGRES_PORT", "5432")
            
            if self.USE_MANAGED_IDENTITY:
                # When using Managed Identity, password will be injected at runtime
                return f"postgresql://{user}@{host}:{port}/{dbname}"
            else:
                password = os.getenv("POSTGRES_PASSWORD", "")
                return f"postgresql://{user}:{password}@{host}:{port}/{dbname}"
        else:
            # Use standard connection string for local development
            return self.DATABASE_URL

# Instantiate the settings object
settings = Settings()

# Override DATABASE_URL with dynamic connection string when deployed to Azure
if settings.AZURE_DEPLOYMENT:
    settings.DATABASE_URL = settings.get_db_connection_string
