from pydantic_settings import BaseSettings
import os

class Settings(BaseSettings):
    #  Database Configuration
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://postgres:admin@localhost/pd_management")
    
    #  Authentication & Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your_secret_key")
    REFRESH_SECRET_KEY: str = os.getenv("REFRESH_SECRET_KEY", "your_refresh_secret_key")  #  Added REFRESH_SECRET_KEY
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 120))

    #  Logging Configuration
    LOG_FILE: str = os.getenv("LOG_FILE", "app.log")
    LOG_BACKUP_COUNT: int = int(os.getenv("LOG_BACKUP_COUNT", 5))

    #  Risk Analysis Settings
    RISK_THRESHOLD: float = float(os.getenv("RISK_THRESHOLD", 1.0))

    #  Seeding Configuration
    RUN_SEEDER: bool = os.getenv("RUN_SEEDER", "true").lower() == "true"

    # HAPI FHIR Server Base url
    HAPI_FHIR_BASE_URL: str = os.getenv("HAPI_BASE_URL", "http://localhost:8080/fhir/")

    class Config:
        env_file = ".env"

#  Instantiate the settings object
settings = Settings()
