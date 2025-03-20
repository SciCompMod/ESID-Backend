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
from app.models.parameter_definition import ParameterDefinition
from security_api import get_token_bearerAuth

from app.controller.parameterdefinitions_controller import ParameterController

router = APIRouter()
controller = ParameterController()


@router.post(
    "/parameterdefinitions",
    responses={
        201: {"model": ID, "description": "Created parameter definition."},
    },
    tags=["ParameterDefinitions"],
    response_model_by_alias=True,
)
async def create_parameter_definition(
    parameter_definition: ParameterDefinition = Body(None, description=""),
    token_bearerAuth: TokenModel = Security(
        get_token_bearerAuth
    ),
) -> ID:
    """Create a new parameter definition."""
    return await controller.create_parameter_definition(parameter_definition)


@router.delete(
    "/parameterdefinitions/{parameterId}",
    responses={
        200: {"description": "Deleted parameter definition."},
        409: {"model": Error, "description": "Preconditions not met. Error contains reason. May have additional properties referenced in error."},
    },
    tags=["ParameterDefinitions"],
    response_model_by_alias=True,
)
async def delete_parameter_definition(
    parameterId: StrictStr = Path(..., description=""),
    token_bearerAuth: TokenModel = Security(
        get_token_bearerAuth
    ),
) -> None:
    """Delete a parameter definition."""
    return await controller.delete_parameter_definition(parameterId)


@router.get(
    "/parameterdefinitions",
    responses={
        200: {"model": List[ParameterDefinition], "description": "Returned list of parameter definitions."},
    },
    tags=["ParameterDefinitions"],
    response_model_by_alias=True,
)
async def list_parameter_definitions(
    token_bearerAuth: TokenModel = Security(
        get_token_bearerAuth
    ),
) -> List[ParameterDefinition]:
    """List all existing Parameter definitions."""
    return await controller.list_parameter_definitions()

@router.get(
    "/parameterdefinitions/{parameterId}",
    responses={
        200: {"model": ParameterDefinition, "description": "Returned specific of parameter definitions."},
    },
    tags=["ParameterDefinitions"],
    response_model_by_alias=True,
)
async def get_parameter_definition(
    parameterId: StrictStr = Path(..., description=""),
    token_bearerAuth: TokenModel = Security(
        get_token_bearerAuth
    ),
) -> ParameterDefinition:
    """Get specific Parameter definitions."""
    return await controller.get_parameter_definition(parameterId)
