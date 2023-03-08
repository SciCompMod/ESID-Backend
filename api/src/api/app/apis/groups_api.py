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
from app.models.group import Group
from app.models.id import ID
from app.models.new_group import NewGroup
from security_api import get_token_bearerAuth
from uuid import uuid4

from app.db.tasks import create_new_group, get_all_group
from app.controller import GroupsController

router = APIRouter()
groups_controller = GroupsController()

@router.post(
    "/groups/",
    responses={
        201: {"model": ID, "description": "node created"},
    },
    tags=["Groups"],
    response_model_by_alias=True,
)
async def create_group(
    new_group: NewGroup = Body(None, description=""),
    token_bearerAuth: TokenModel = Security(
        get_token_bearerAuth
    ),
) -> ID:
    return groups_controller.create_group(new_group)


@router.delete(
    "/groups/{group_id}/",
    responses={
        202: {"description": "Group deleted"},
    },
    tags=["Groups"],
    response_model_by_alias=True,
)
async def delete_group(
    group_id: str = Path(None, description=""),
    token_bearerAuth: TokenModel = Security(
        get_token_bearerAuth
    ),
) -> None:
    """deletes the Group if it is not referenced in any list"""
    return groups_controller.delete_group(group_id)


@router.get(
    "/groups/{group_id}/",
    responses={
        200: {"model": Group, "description": "return the Group"},
    },
    tags=["Groups"],
    response_model_by_alias=True,
)
async def get_group(
    group_id: str = Path(None, description=""),
    token_bearerAuth: TokenModel = Security(
        get_token_bearerAuth
    ),
) -> Group:
    return groups_controller.get_group_by_id(group_id)


@router.get(
    "/groups/",
    responses={
        200: {"model": List[str], "description": "return the list of existing groups"},
    },
    tags=["Groups"],
    response_model_by_alias=True,
)
async def list_groups(
    token_bearerAuth: TokenModel = Security(
        get_token_bearerAuth
    ),
) -> List[str]:
    return groups_controller.get_all_groups()
