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
from app.models.id import ID
from app.models.model import Model
from app.models.new_model import NewModel
from security_api import get_token_bearerAuth
from app.controller.model_controller import ModelsController

router = APIRouter()
model_controller = ModelsController()

@router.post(
    "/models",
    responses={
        200: {"model": ID, "description": "create a new Model"},
    },
    tags=["Models"],
    response_model_by_alias=True,
)
async def create_model(
    new_model: NewModel = Body(None, description=""),
    token_bearerAuth: TokenModel = Security(
        get_token_bearerAuth
    ),
) -> ID:
    return model_controller.create_new_model(new_model=new_model)


@router.delete(
    "/models/{model_id}",
    responses={
        202: {"description": "Model deleted"},
    },
    tags=["Models"],
    response_model_by_alias=True,
)
async def delete_model(
    model_id: str = Path(None, description=""),
    token_bearerAuth: TokenModel = Security(
        get_token_bearerAuth
    ),
) -> None:
    """deletes the model if it is not referenced in any scenario"""
    return model_controller.delete_model_by_id(model_id=model_id)


@router.get(
    "/models/{model_id}",
    responses={
        200: {"model": Model, "description": "return the list of Models"},
    },
    tags=["Models"],
    response_model_by_alias=True,
)
async def get_model(
    model_id: str = Path(None, description=""),
    token_bearerAuth: TokenModel = Security(
        get_token_bearerAuth
    ),
) -> Model:
    return model_controller.get_model_by_id(model_id)


@router.get(
    "/models",
    responses={
        200: {"model": List[str], "description": "return the list of Models"},
    },
    tags=["Models"],
    response_model_by_alias=True,
)
async def list_models(
    token_bearerAuth: TokenModel = Security(
        get_token_bearerAuth
    ),
) -> List[str]:
    return model_controller.get_all_models()
