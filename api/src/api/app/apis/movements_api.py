# coding: utf-8

from typing import Dict, List  # noqa: F401

from fastapi import (  # noqa: F401
    APIRouter,
    Body,
    Cookie,
    Depends,
    Form,
    Header,
    Path,
    Query,
    Response,
    Security,
    status,
)

from app.models.extra_models import TokenModel  # noqa: F401
from security_api import get_token_bearerAuth

router = APIRouter()


@router.get(
    "/movements/",
    responses={
        200: {"model": List[str], "description": "return the account"},
    },
    tags=["Movements"],
    response_model_by_alias=True,
)
async def list_movements(
    token_bearerAuth: TokenModel = Security(
        get_token_bearerAuth
    ),
) -> List[str]:
    ...
