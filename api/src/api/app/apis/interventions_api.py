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
from app.models.intervention import Intervention
from app.models.new_intervention import NewIntervention
from fastapi.security import HTTPBearer
from security_api import get_token_bearerAuth
from uuid import uuid4

from app.db.tasks import create_new_intervention, get_all_interventions, get_intervention_by_id, delete_intervention_by_id

router = APIRouter()
# get_token_bearerAuth = HTTPBearer()

@router.post(
    "/interventions/",
    responses={
        201: {"model": ID, "description": "Intervention created"},
    },
    tags=["Interventions"],
    response_model_by_alias=True,
)

async def create_intervention(
    new_intervention: NewIntervention = Body(None, description=""),
    token_bearerAuth: TokenModel = Security(
        get_token_bearerAuth
    ),
) -> ID:
    intervention_id = str(uuid4())
    create_new_intervention(new_intervention.name, new_intervention.description, intervention_id)
    return ID(id=intervention_id)


@router.delete(
    "/interventions/{intervention_id}/",
    responses={
        202: {"description": "Node deleted"},
    },
    tags=["Interventions"],
    response_model_by_alias=True,
)
async def delete_intervention(
    intervention_id: str = Path(None, description=""),
    token_bearerAuth: TokenModel = Security(
        get_token_bearerAuth
    ),
) -> None:
    """deletes the Intervention if it is not referenced in any list"""
    delete_intervention_by_id(intervention_id)
    return {"Intervention deleted"}


@router.get(
    "/interventions/{intervention_id}/",
    responses={
        200: {"model": Intervention, "description": "return the Node"},
    },
    tags=["Interventions"],
    response_model_by_alias=True,
)
async def get_intervention(
    intervention_id: str = Path(None, description=""),
    token_bearerAuth: TokenModel = Security(
        get_token_bearerAuth
    ),
) -> Intervention:
    intervention_info = get_intervention_by_id(intervention_id)
    return Intervention(name=intervention_info.name, description=intervention_info.description, id=intervention_info.id)

@router.get(
    "/interventions/",
    responses={
        200: {"model": List[str], "description": "return the list of available interventions"},
    },
    tags=["Interventions"],
    response_model_by_alias=True,
)
async def list_interventions(
    token_bearerAuth: TokenModel = Security(
        get_token_bearerAuth
    ),

) -> List[str]:
    interventions = get_all_interventions()
    try: 
        intervention_ids = [intervention.id for intervention in interventions]
        return intervention_ids
    except TypeError:
        return {"No interventions available"}
