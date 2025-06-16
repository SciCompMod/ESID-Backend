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
    Path,
    Query,
    Response,
    Security,
    status,
)

from app.models.extra_models import TokenModel  # noqa: F401
from app.models.error import Error
from app.models.id import ID
from app.models.intervention_template import InterventionTemplate

from app.controller.interventions_controller import InterventionsController

router = APIRouter()
controller = InterventionsController()

@router.post(
    "/interventions/templates",
    responses={
        201: {"model": ID, "description": "Intervention created."},
    },
    tags=["Interventions"],
    response_model_by_alias=True,
)
async def create_intervention_template(
    intervention_template: InterventionTemplate = Body(None, description="")
) -> ID:
    """Creates a new intervention template to be used in implementations."""
    return await controller.create_intervention_template(intervention_template)


@router.delete(
    "/interventions/templates/{interventionTemplateId}",
    responses={
        200: {"description": "Deleted template."},
        409: {"model": Error, "description": "Preconditions not met. Error contains reason. May have additional properties referenced in error."},
    },
    tags=["Interventions"],
    response_model_by_alias=True,
)
async def delete_intervention_template(
    interventionTemplateId: StrictStr = Path(..., description="")
) -> None:
    """Delete an intervention template."""
    return await controller.delete_intervention_template(interventionTemplateId)


@router.get(
    "/interventions/templates",
    responses={
        200: {"model": List[InterventionTemplate], "description": "Returned the list of available templates."},
    },
    tags=["Interventions"],
    response_model_by_alias=True,
)
async def list_intervention_templates() -> List[InterventionTemplate]:
    """List available Intervention templates that can be implemented."""
    return await controller.list_intervention_templates()
