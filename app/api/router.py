from collections.abc import Callable
from typing import Any, get_origin

from fastapi import APIRouter

from app.schemas.response import APIResponse


class APIRouterV1(APIRouter):
    def add_api_route(
        self, path: str, endpoint: Callable[..., Any], **kwargs: Any
    ) -> None:
        response_model = kwargs.get("response_model")
        if response_model and get_origin(response_model) is not APIResponse:
            kwargs["response_model"] = APIResponse[response_model]  # type: ignore

        super().add_api_route(path, endpoint, **kwargs)
