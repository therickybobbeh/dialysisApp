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
from app.api.patient import router as patient_router
from app.api.provider import router as provider_router
from app.db.session import Base, engine
from app.core.logging_config import logger
from datetime import datetime

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
app.include_router(patient_router)
app.include_router(provider_router)



#  Health Check Route
@app.get("/healthcheck", tags=["App health check"])
def health_check():
    return {"message": "Backend is running!"}

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