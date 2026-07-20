import time
import uuid
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from app.core.config import settings
from app.core.logging import get_logger
from app.core.metrics import HTTP_REQUESTS_TOTAL, HTTP_REQUEST_LATENCY

logger = get_logger("app.middleware")

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Generate or extract unique Correlation/Request ID
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        request.state.request_id = request_id

        start_time = time.time()
        endpoint = request.url.path
        method = request.method

        logger.info(
            f"START {method} {endpoint} from {request.client.host if request.client else 'unknown'}",
            extra={"request_id": request_id}
        )

        try:
            response = await call_next(request)
            process_time = time.time() - start_time
            process_time_ms = process_time * 1000
            
            # Attach trace headers to response
            response.headers["X-Request-ID"] = request_id
            response.headers["X-Process-Time-Ms"] = f"{process_time_ms:.2f}"
            
            # Record Prometheus metrics
            HTTP_REQUESTS_TOTAL.labels(method=method, endpoint=endpoint, status=str(response.status_code)).inc()
            HTTP_REQUEST_LATENCY.labels(method=method, endpoint=endpoint).observe(process_time)

            logger.info(
                f"COMPLETE {method} {endpoint} - Status: {response.status_code} - Duration: {process_time_ms:.2f}ms",
                extra={"request_id": request_id}
            )
            return response
        except Exception as exc:
            process_time = time.time() - start_time
            process_time_ms = process_time * 1000
            
            # Record failed request counts
            HTTP_REQUESTS_TOTAL.labels(method=method, endpoint=endpoint, status="500").inc()
            HTTP_REQUEST_LATENCY.labels(method=method, endpoint=endpoint).observe(process_time)

            logger.error(
                f"FAILED {method} {endpoint} - Error: {str(exc)} - Duration: {process_time_ms:.2f}ms",
                exc_info=True,
                extra={"request_id": request_id}
            )
            raise exc

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        
        # Security Hardening response headers configuration
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: https:; "
            "connect-src 'self' ws: wss: http: https:;"
        )
        response.headers["Strict-Transport-Security"] = "max-age=63072000; includeSubDomains; preload"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        
        return response

def setup_middlewares(app: FastAPI):
    # CORS Configuration
    origins = ["*"]
    if settings.APP_ENV == "production":
        origins = [
            "http://localhost:3000",
            "http://127.0.0.1:3000",
            "http://localhost:8000"
        ]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Logging Middleware (Must be applied before SecurityHeaders to capture stats correctly)
    app.add_middleware(RequestLoggingMiddleware)
    
    # Security Headers Middleware
    app.add_middleware(SecurityHeadersMiddleware)
