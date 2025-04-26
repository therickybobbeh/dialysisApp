from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from jose import jwt, JWTError
from app.core.config import settings
from app.core.security import get_current_user
from app.api.auth import router as auth_router
from app.api.dialysis import router as dialysis_router
from app.api.analytics import router as analytics_router
from app.api.provider import router as provider_router
from app.db.session import Base, engine
from app.core.logging_config import logger
from datetime import datetime
from sqlalchemy.orm import Session
from typing import Annotated
import os

#  Ensure database tables exist
Base.metadata.create_all(bind=engine)

# Create FastAPI App
app = FastAPI()

#  CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

#  Register API Routers
app.include_router(auth_router, prefix="/auth", tags=["Authentication"])
app.include_router(dialysis_router) 
app.include_router(analytics_router)
app.include_router(provider_router)



#  Health Check Route
@app.get("/health", status_code=200, tags=["Health"])
async def health_check(db: Annotated[Session, Depends(get_db)]):
    """
    Health check endpoint for container health probes.
    This endpoint checks the application's health including database connectivity.
    
    Returns:
        dict: Health check status
    """
    health_data = {
        "status": "healthy",
        "version": os.getenv("APP_VERSION", "1.0.0"),
        "timestamp": datetime.now().isoformat(),
        "checks": {
            "app": "healthy"
        }
    }
    
    # Check database connectivity if enabled
    if settings.HEALTH_CHECK_INCLUDE_DB:
        try:
            # Execute simple query to verify DB connection
            db.execute("SELECT 1")
            health_data["checks"]["database"] = "connected"
        except Exception as e:
            health_data["status"] = "unhealthy"
            health_data["checks"]["database"] = str(e)
    
    # Check Application Insights if enabled
    if settings.ENABLE_APP_INSIGHTS:
        try:
            if settings.APPLICATION_INSIGHTS_CONNECTION_STRING:
                health_data["checks"]["app_insights"] = "configured"
            else:
                health_data["checks"]["app_insights"] = "missing connection string"
        except Exception as e:
            health_data["checks"]["app_insights"] = str(e)
    
    # Return 500 status code if unhealthy
    if health_data["status"] != "healthy":
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=health_data
        )
    
    return health_data

#  Global Exception Handling
@app.exception_handler(Exception)
def global_exception_handler(request, exc):
    logger.error(f"Unhandled exception: {str(exc)}")
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    return JSONResponse(status_code=400, content={"detail": exc.errors()})

#  JWT Authentication Function
def verify_jwt_token(token: str):
    """ Validate JWT Token """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload.get("sub")  # Return the user email
    except JWTError as e:
        logger.error(f" JWT validation error: {str(e)}")
        return None

#  Replace WebSockets with Polling API
live_data = {"last_update": str(datetime.utcnow()), "dialysis_status": "stable"}