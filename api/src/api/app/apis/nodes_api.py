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
from app.models.new_node import NewNode
from app.models.new_node_list import NewNodeList
from app.models.node_list import NodeList
from app.models.node import Node
from security_api import get_token_bearerAuth
from app.controller.nodes_controller import NodesController

router = APIRouter()
nodes_controller = NodesController()


@router.post(
    "/nodes/",
    responses={
        201: {"model": ID, "description": "node created"},
    },
    tags=["Nodes"],
    response_model_by_alias=True,
)
async def create_node(
    new_node: NewNode = Body(None, description=""),
    token_bearerAuth: TokenModel = Security(
        get_token_bearerAuth
    ),
) -> ID:
    return nodes_controller.create_new_node(new_node)


@router.post(
    "/nodelists/",
    responses={
        201: {"model": ID, "description": "node list created"},
    },
    tags=["Nodes"],
    response_model_by_alias=True,
)
async def create_node_list(
    new_nodelists: NewNodeList = Body(None, description=""),
    token_bearerAuth: TokenModel = Security(
        get_token_bearerAuth
    ),
) -> ID:
    return nodes_controller.create_new_nodelist(new_nodelists)


@router.delete(
    "/nodes/{node_id}/",
    responses={
        202: {"description": "Node deleted"},
    },
    tags=["Nodes"],
    response_model_by_alias=True,
)
async def delete_node(
    node_id: str = Path(None, description=""),
    token_bearerAuth: TokenModel = Security(
        get_token_bearerAuth
    ),
) -> None:
    """deletes the node if it is not referenced in any list"""
    return nodes_controller.delete_node_by_id(node_id=node_id)


@router.delete(
    "/nodelists/{nodelist_id}/",
    responses={
        202: {"description": "NodeList deleted"},
    },
    tags=["Nodes"],
    response_model_by_alias=True,
)
async def delete_node_list(
    nodelist_id: str = Path(None, description=""),
    token_bearerAuth: TokenModel = Security(
        get_token_bearerAuth
    ),
) -> None:
    """deletes the node list"""
    return nodes_controller.delete_nodelist_by_id(nodelist_id)


@router.get(
    "/nodes/{node_id}/",
    responses={
        200: {"model": Node, "description": "return the Node"},
    },
    tags=["Nodes"],
    response_model_by_alias=True,
)
async def get_node(
    node_id: str = Path(None, description=""),
    token_bearerAuth: TokenModel = Security(
        get_token_bearerAuth
    ),
) -> Node:
    return nodes_controller.get_node_by_id(node_id=node_id)


@router.get(
    "/nodelists/{nodelist_id}/",
    responses={
        200: {"model": List[str], "description": "return the Node"},
    },
    tags=["Nodes"],
    response_model_by_alias=True,
)
async def get_node_list(
    nodelist_id: str = Path(None, description=""),
    token_bearerAuth: TokenModel = Security(
        get_token_bearerAuth
    ),
) -> List[str]:
    print("Node api")
    print("*" *100)
    return nodes_controller.get_nodelist_by_id(nodelist_id=nodelist_id)


@router.get(
    "/nodelists/",
    responses={
        200: {"model": NewNodeList, "description": "return all defined nodelists"},
    },
    tags=["Nodes"],
    response_model_by_alias=True,
)
async def get_node_lists(
    token_bearerAuth: TokenModel = Security(
        get_token_bearerAuth
    ),
) -> NewNodeList:
    return nodes_controller.get_all_nodelists()


@router.get(
    "/nodes/",
    responses={
        200: {"model": List[str], "description": "return the account"},
    },
    tags=["Nodes"],
    response_model_by_alias=True,
)
async def list_nodes(
    token_bearerAuth: TokenModel = Security(
        get_token_bearerAuth
    ),
) -> List[str]:
    return nodes_controller.get_all_nodes()
