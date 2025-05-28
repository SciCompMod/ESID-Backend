# coding: utf-8

from typing import Dict, List  # noqa: F401
from pydantic import StrictStr
from typing import Any, List, Optional
from fastapi import (  # noqa: F401
    APIRouter,
    Body,
    Cookie,
    Depends,
    Form,
    Header,
    HTTPException,
    Path,
    Query,
    Response,
    Security,
    status,
)

from app.models.extra_models import TokenModel  # noqa: F401
from app.models.error import Error
from app.models.id import ID
from app.models.model import Model
from app.models.reduced_info import ReducedInfo

from app.controller.models_controller import ModelController

router = APIRouter()
controller = ModelController()

@router.post(
    "/models",
    responses={
        200: {"model": ID, "description": "Created new model."},
    },
    tags=["Models"],
    response_model_by_alias=True,
)
async def create_model(
    model: Model = Body(None, description="")
) -> ID:
    """Create a new simulation model."""
    return await controller.create_model(model)


@router.delete(
    "/models/{modelId}",
    responses={
        200: {"description": "Model deleted."},
        409: {"model": Error, "description": "Preconditions not met. Error contains reason. May have additional properties referenced in error."},
    },
    tags=["Models"],
    response_model_by_alias=True,
)
async def delete_model(
    modelId: StrictStr = Path(..., description="")
) -> None:
    """Delete a model if it is not referenced in any scenarios."""
    return await controller.delete_model(modelId)


@router.get(
    "/models/{modelId}",
    responses={
        200: {"model": Model, "description": "Returned the list of Models."},
    },
    tags=["Models"],
    response_model_by_alias=True,
)
async def get_model(
    modelId: StrictStr = Path(..., description="")
) -> Model:
    """Get specific model information."""
    return await controller.get_model(modelId)


@router.get(
    "/models",
    responses={
        200: {"model": List[ReducedInfo], "description": "Returned list of models."},
    },
    tags=["Models"],
    response_model_by_alias=True,
)
async def list_models() -> List[ReducedInfo]:
    """List all available simulation models."""
    return await controller.list_models()
