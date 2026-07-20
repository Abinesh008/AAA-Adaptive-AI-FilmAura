import sys
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger("app.core.env_validation")

def validate_environment():
    """
    Validates required environment variables at application startup.
    Raises ValueError and stops execution if validation fails in production mode.
    """
    errors = []

    # If running in production mode, enforce strong checks
    if settings.APP_ENV == "production":
        # 1. Check database passwords
        if settings.POSTGRES_PASSWORD == "password":
            errors.append("POSTGRES_PASSWORD cannot be 'password' in production.")
        
        if settings.NEO4J_PASSWORD == "password":
            errors.append("NEO4J_PASSWORD cannot be 'password' in production.")

        # 2. Check API keys if provider is set
        if settings.LLM_PROVIDER == "openai":
            if not settings.OPENAI_API_KEY or settings.OPENAI_API_KEY == "mock-openai-api-key":
                errors.append("OPENAI_API_KEY must be configured when LLM_PROVIDER is set to 'openai' in production.")
        elif settings.LLM_PROVIDER == "gemini":
            if not settings.GEMINI_API_KEY or settings.GEMINI_API_KEY == "mock-gemini-api-key":
                errors.append("GEMINI_API_KEY must be configured when LLM_PROVIDER is set to 'gemini' in production.")

    if errors:
        logger.error("!!! ENVIRONMENT VARIABLE VALIDATION FAILED !!!")
        for err in errors:
            logger.error(f" - {err}")
        # Terminate startup with clear error
        sys.exit(1)

    logger.info(f"Environment variables successfully validated (Env: {settings.APP_ENV})")
