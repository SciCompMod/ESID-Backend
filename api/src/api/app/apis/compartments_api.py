# coding: utf-8

from typing import Dict, List  # noqa: F401

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

from pydantic import StrictStr
from typing import Any, List, Optional

from app.models.extra_models import TokenModel  # noqa: F401
from app.models.error import Error
from app.models.id import ID
from app.models.compartment import Compartment
from security_api import get_token_bearerAuth

from app.controller.compartments_controller import CompartmentController

router = APIRouter()
controller = CompartmentController

@router.post(
    "/compartments",
    responses={
        201: {"model": ID, "description": "Created compartment."},
    },
    tags=["Compartments"],
    response_model_by_alias=True,
)
async def create_compartment(
    compartment: Optional[Compartment] = Body(None, description=""),
    token_bearerAuth: TokenModel = Security(
        get_token_bearerAuth
    ),
) -> ID:
    """Create a new compartment."""
    return await controller.create_compartment(compartment)


@router.delete(
    "/compartments/{compartmentId}",
    responses={
        200: {"description": "Deleted compartment."},
        409: {"model": Error, "description": "Preconditions not met. Error contains reason. May have additional properties referenced in error."},
    },
    tags=["Compartments"],
    response_model_by_alias=True,
)
async def delete_compartment(
    compartmentId: StrictStr = Path(..., description=""),
    token_bearerAuth: TokenModel = Security(
        get_token_bearerAuth
    ),
) -> None:
    """Delete specific compartment."""
    return await controller.delete_compartment(compartmentId)


@router.get(
    "/compartments",
    responses={
        200: {"model": List[Compartment], "description": "Returned the list of compartments."},
    },
    tags=["Compartments"],
    response_model_by_alias=True,
)
async def list_compartments(
    token_bearerAuth: TokenModel = Security(
        get_token_bearerAuth
    ),
) -> List[Compartment]:
    """List all existing compartments."""
    return await controller.list_compartments()
