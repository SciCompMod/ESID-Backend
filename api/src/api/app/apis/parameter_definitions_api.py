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
from app.models.new_parameter_definition import NewParameterDefinition
from app.models.parameter_definition import ParameterDefinition
from security_api import get_token_bearerAuth
from uuid import uuid4

# TODO: Call from controller, avoid importing from tasks
from app.db.tasks import create_new_parameter_definition, get_all_parameter_definitions, get_parameter_definition_by_id, delete_parameter_definition_by_id

router = APIRouter()


@router.post(
    "/parameterdefinitions/",
    responses={
        201: {"model": ID, "description": "node created"},
    },
    tags=["ParameterDefinitions"],
    response_model_by_alias=True,
)
async def create_parameter_definition(
    new_parameter_definition: NewParameterDefinition = Body(None, description=""),
    token_bearerAuth: TokenModel = Security(
        get_token_bearerAuth
    ),
) -> ID:
    parameter_definition_id = str(uuid4())
    create_new_parameter_definition(new_parameter_definition.name, new_parameter_definition.description, parameter_definition_id)
    return ID(id=parameter_definition_id)


@router.delete(
    "/parameterdefinitions/{parameter_id}/",
    responses={
        202: {"description": "Group deleted"},
    },
    tags=["ParameterDefinitions"],
    response_model_by_alias=True,
)
async def delete_parameter_definition(
    parameter_id: str = Path(None, description=""),
    token_bearerAuth: TokenModel = Security(
        get_token_bearerAuth
    ),
) -> None:
    """deletes the Group if it is not referenced in any list"""
    delete_parameter_definition_by_id(parameter_id)
    return {"Parameter definition deleted"}


@router.get(
    "/parameterdefinitions/{parameter_id}/",
    responses={
        200: {"model": ParameterDefinition, "description": "return the Group"},
    },
    tags=["ParameterDefinitions"],
    response_model_by_alias=True,
)
async def get_parameter_definition(
    parameter_id: str = Path(None, description=""),
    token_bearerAuth: TokenModel = Security(
        get_token_bearerAuth
    ),
) -> ParameterDefinition:
    parameter_definition_info = get_parameter_definition_by_id(parameter_id)
    return ParameterDefinition(name=parameter_definition_info.name, description=parameter_definition_info.description, id=parameter_definition_info.id)


@router.get(
    "/parameterdefinitions/",
    responses={
        200: {"model": List[str], "description": "return the list of existing Parameter Definitions"},
    },
    tags=["ParameterDefinitions"],
    response_model_by_alias=True,
)
async def list_parameter_definitions(
    token_bearerAuth: TokenModel = Security(
        get_token_bearerAuth
    ),
) -> List[str]:
    parameter_definitions = get_all_parameter_definitions()
    try:
        parameter_definition_ids = [parameter.id for parameter in parameter_definitions]
        return parameter_definition_ids
    except TypeError:
        return {"No parameter definitions available"}
