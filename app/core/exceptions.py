import structlog
from fastapi import HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

logger = structlog.get_logger("api.exceptions")


async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    status_code = 500
    detail = "Internal Server Error"
    payload = None

    if isinstance(exc, HTTPException):
        status_code = exc.status_code
        detail = exc.detail

    elif isinstance(exc, RequestValidationError):
        status_code = 422
        detail = "Validation Error"
        payload = exc.errors()

    else:
        logger.bind(
            method=request.method,
            path=request.url.path,
            client_host=request.client.host if request.client else None,
        ).error(
            "Unhandled Exception",
            exc_info=True,
            error=str(exc),
        )

    return JSONResponse(
        status_code=status_code,
        content={
            "code": status_code,
            "message": detail,
            "payload": payload,
        },
    )
