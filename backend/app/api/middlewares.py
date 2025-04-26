"""
Middleware for request tracking, correlation IDs, and request logging.
Provides integration with Application Insights for distributed tracing.
"""

import time
import logging
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from app.core.logging_config import get_request_id

logger = logging.getLogger(__name__)

class RequestTrackingMiddleware(BaseHTTPMiddleware):
    """
    Middleware for request tracking, logging, and correlation IDs.
    Adds correlation ID headers for distributed tracing and logs request/response details.
    """
    
    async def dispatch(self, request: Request, call_next):
        # Generate unique correlation ID for this request
        correlation_id = request.headers.get("x-correlation-id", get_request_id())
        request_id = get_request_id()
        
        # Add correlation ID to request state for use in route handlers
        request.state.correlation_id = correlation_id
        request.state.request_id = request_id
        
        # Add user ID if available from auth header
        user_id = None
        if "authorization" in request.headers:
            # In a real app, you'd extract user ID from the token 
            # This is just a placeholder
            user_id = "authenticated_user"  
        request.state.user_id = user_id
        
        # Log request start with extra data for structured logging
        logger_extra = {
            "request_id": request_id,
            "correlation_id": correlation_id,
            "user_id": user_id,
        }
        
        start_time = time.time()
        
        # Log incoming request with path and method
        logger.info(
            f"Request started: {request.method} {request.url.path}", 
            extra=logger_extra
        )
        
        # Process the request and capture any exceptions
        try:
            response = await call_next(request)
            
            # Add correlation ID header to response for client tracing
            response.headers["X-Correlation-ID"] = correlation_id
            response.headers["X-Request-ID"] = request_id
            
            # Calculate processing time
            process_time = time.time() - start_time
            response.headers["X-Process-Time"] = str(process_time)
            
            # Log completion with status code and processing time
            logger.info(
                f"Request completed: {request.method} {request.url.path} - Status: {response.status_code} - Time: {process_time:.3f}s",
                extra=logger_extra
            )
            
            return response
        
        except Exception as e:
            # Log exceptions with full details
            process_time = time.time() - start_time
            logger.exception(
                f"Request failed: {request.method} {request.url.path} - Error: {str(e)} - Time: {process_time:.3f}s",
                extra=logger_extra
            )
            raise  # Re-raise for FastAPI's exception handlers