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
from app.models.group import Group
from app.models.id import ID

from app.controller.groups_controller import GroupsController

router = APIRouter()
controller = GroupsController()

@router.post(
    "/groups",
    responses={
        201: {"model": ID, "description": "Created group."},
    },
    tags=["Groups"],
    response_model_by_alias=True,
)
async def create_group(
    group: Group = Body(None, description="")
) -> ID:
    """Create a new (stratification) group. All groups with the same category are mutually exclusive."""
    return await controller.create(group)


@router.delete(
    "/groups/{groupId}",
    responses={
        200: {"description": "Group deleted."},
        409: {"model": Error, "description": "Preconditions not met. Error contains reason. May have additional properties referenced in error."},
    },
    tags=["Groups"],
    response_model_by_alias=True,
)
async def delete_group(
    groupId: StrictStr = Path(..., description="")
) -> None:
    """Delete the specified group."""
    return await controller.delete(groupId)


@router.get(
    "/groups",
    responses={
        200: {"model": List[Group], "description": "Returned list of existing groups"},
    },
    tags=["Groups"],
    response_model_by_alias=True,
)
async def list_groups() -> List[Group]:
    """List all (stratification) groups."""
    return await controller.getAll()


@router.get(
    "/groups/categories/",
    responses={
        200: {"model": List[str], "description": "Returned list of existing categories."},
    },
    tags=["Groups"],
    response_model_by_alias=True,
)
async def list_categories() -> List[str]:
    """List all existing categories."""
    return await controller.getCategories()
