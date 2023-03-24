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
from app.models.aggregation import Aggregation
from app.models.id import ID
from app.models.new_aggregation import NewAggregation
from security_api import get_token_bearerAuth

from app.controller.aggregations_controller import AggregationsController

router = APIRouter()
aggregation_controller = AggregationsController()


@router.post(
    "/aggregations",
    responses={
        201: {"model": ID, "description": "aggregation created"},
    },
    tags=["Aggregations"],
    response_model_by_alias=True,
)
async def create_aggregations(
    new_aggregation: NewAggregation = Body(None, description=""),
    token_bearerAuth: TokenModel = Security(
        get_token_bearerAuth
    ),
) -> ID:
    aggregation_id = aggregation_controller.create_new_aggregation(new_aggregation)
    return aggregation_id


@router.delete(
    "/aggregations/{aggregations_id}",
    responses={
        202: {"description": "Group deleted"},
    },
    tags=["Aggregations"],
    response_model_by_alias=True,
)
async def delete_aggregation(
    aggregations_id: str = Path(None, description=""),
    token_bearerAuth: TokenModel = Security(
        get_token_bearerAuth
    ),
) -> None:
    """deletes the Group if it is not referenced in any list"""
    return aggregation_controller.delete_aggregation_by_id(aggregations_id)


@router.get(
    "/aggregations/{aggregations_id}",
    responses={
        200: {"model": Aggregation, "description": "return the Group"},
    },
    tags=["Aggregations"],
    response_model_by_alias=True,
)
async def get_aggregations(
    aggregations_id: str = Path(None, description=""),
    token_bearerAuth: TokenModel = Security(
        get_token_bearerAuth
    ),
) -> Aggregation:
    return aggregation_controller.get_aggregation_by_id(aggregations_id)


@router.get(
    "/aggregations",
    responses={
        200: {"model": List[str], "description": "return the list of existing aggregations"},
    },
    tags=["Aggregations"],
    response_model_by_alias=True,
)
async def list_aggregations(
    token_bearerAuth: TokenModel = Security(
        get_token_bearerAuth
    ),
) -> List[str]:
    return aggregation_controller.get_all_aggregations()
