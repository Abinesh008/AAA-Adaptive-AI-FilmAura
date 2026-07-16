from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from app.core.logging import get_logger

logger = get_logger("app.exceptions")

# Base Application Exception
class FilmAuraException(Exception):
    def __init__(self, message: str, code: str = "INTERNAL_SERVER_ERROR", status_code: int = 500, details: dict | None = None):
        super().__init__(message)
        self.message = message
        self.code = code
        self.status_code = status_code
        self.details = details or {}

# Domain/Core Exceptions
class EntityNotFoundException(FilmAuraException):
    def __init__(self, message: str, details: dict | None = None):
        super().__init__(message, code="ENTITY_NOT_FOUND", status_code=status.HTTP_404_NOT_FOUND, details=details)

class ConfigurationException(FilmAuraException):
    def __init__(self, message: str):
        super().__init__(message, code="CONFIGURATION_ERROR", status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

class AIProviderException(FilmAuraException):
    def __init__(self, message: str, details: dict | None = None):
        super().__init__(message, code="AI_PROVIDER_ERROR", status_code=status.HTTP_502_BAD_GATEWAY, details=details)

class DatabaseException(FilmAuraException):
    def __init__(self, message: str, details: dict | None = None):
        super().__init__(message, code="DATABASE_ERROR", status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, details=details)

class RateLimitException(FilmAuraException):
    def __init__(self, message: str = "Rate limit exceeded. Please try again later."):
        super().__init__(message, code="RATE_LIMIT_EXCEEDED", status_code=status.HTTP_429_TOO_MANY_REQUESTS)


# Exception handler registration helper
def setup_exception_handlers(app: FastAPI):
    
    @app.exception_handler(FilmAuraException)
    async def filmaura_exception_handler(request: Request, exc: FilmAuraException):
        logger.error(f"AppError [{exc.code}]: {exc.message} - Details: {exc.details}")
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "success": False,
                "error": {
                    "code": exc.code,
                    "message": exc.message,
                    "details": exc.details
                }
            }
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        details = {"errors": exc.errors()}
        logger.warning(f"ValidationError: {str(exc)}")
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "success": False,
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": "Input validation failed.",
                    "details": details
                }
            }
        )

    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        logger.exception(f"Unhandled Exception: {str(exc)}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "success": False,
                "error": {
                    "code": "INTERNAL_SERVER_ERROR",
                    "message": "An unexpected error occurred on the server.",
                    "details": {"exception": str(exc)} if app.debug else {}
                }
            }
        )
