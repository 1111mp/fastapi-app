from fastapi import status
from pydantic import BaseModel, ConfigDict


class APIResponse[T](BaseModel):
    """API response model."""

    model_config = ConfigDict(
        from_attributes=True,
    )

    code: int = status.HTTP_200_OK
    message: str = "OK"
    payload: T | None = None
