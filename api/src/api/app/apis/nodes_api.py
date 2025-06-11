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
from app.models.node import Node
from app.models.node_list import NodeList, NodeListWithNodes
from app.models.reduced_info import ReducedInfo
from security_api import get_token_bearerAuth

from app.controller.nodes_controller import NodeController

router = APIRouter()
controller = NodeController()


@router.post(
    "/nodes",
    status_code=201,
    responses={
        201: {"model": ID, "description": "node created"},
    },
    tags=["Nodes"],
    response_model_by_alias=True,
)
async def create_node(
    node: Node = Body(None, description=""),
    token_bearerAuth: TokenModel = Security(
        get_token_bearerAuth
    ),
) -> ID:
    """Create a new node."""
    return await controller.create_node(node)


@router.post(
    "/nodelists",
    status_code=201,
    responses={
        201: {"model": ID, "description": "Created node list."},
    },
    tags=["Nodes"],
    response_model_by_alias=True,
)
async def create_node_list(
    node_list: NodeList = Body(None, description=""),
    token_bearerAuth: TokenModel = Security(
        get_token_bearerAuth
    ),
) -> ID:
    """Create a new node list."""
    return await controller.create_node_list(node_list)


@router.delete(
    "/nodes/{nodeId}",
    responses={
        200: {"description": "Deleted node."},
        409: {"model": Error, "description": "Preconditions not met. Error contains reason. May have additional properties referenced in error."},
    },
    tags=["Nodes"],
    response_model_by_alias=True,
)
async def delete_node(
    nodeId: StrictStr = Path(..., description=""),
    token_bearerAuth: TokenModel = Security(
        get_token_bearerAuth
    ),
) -> None:
    """Delete a node."""
    return await controller.delete_node(nodeId)


@router.delete(
    "/nodelists/{nodeListId}",
    responses={
        200: {"description": "Deleted node list."},
        409: {"model": Error, "description": "Preconditions not met. Error contains reason. May have additional properties referenced in error."},
    },
    tags=["Nodes"],
    response_model_by_alias=True,
)
async def delete_node_list(
    nodeListId: StrictStr = Path(..., description=""),
    token_bearerAuth: TokenModel = Security(
        get_token_bearerAuth
    ),
) -> None:
    """Delete the specified node list."""
    return await controller.delete_node_list(nodeListId)


@router.get(
    "/nodelists/{nodeListId}",
    responses={
        200: {"model": NodeListWithNodes, "description": "Returned the node list."},
    },
    tags=["Nodes"],
    response_model_by_alias=True,
)
async def get_node_list(
    nodeListId: StrictStr = Path(..., description=""),
    token_bearerAuth: TokenModel = Security(
        get_token_bearerAuth
    ),
) -> NodeListWithNodes:
    """Get specified node list."""
    return await controller.get_node_list(nodeListId)


@router.get(
    "/nodelists",
    responses={
        200: {"model": List[ReducedInfo], "description": "Returned all defined node lists"},
    },
    tags=["Nodes"],
    response_model_by_alias=True,
)
async def list_node_lists(
    token_bearerAuth: TokenModel = Security(
        get_token_bearerAuth
    ),
) -> List[ReducedInfo]:
    """List defined node lists."""
    return await controller.list_node_lists()


@router.get(
    "/nodes",
    responses={
        200: {"model": List[Node], "description": "Returned list of nodes"},
    },
    tags=["Nodes"],
    response_model_by_alias=True,
)
async def list_nodes(
    token_bearerAuth: TokenModel = Security(
        get_token_bearerAuth
    ),
) -> List[Node]:
    """List all available nodes."""
    return await controller.list_nodes()
