# coding: utf-8

from typing import ClassVar, Dict, List, Tuple  # noqa: F401
from fastapi import HTTPException

from pydantic import StrictStr
from typing import Any, List, Optional
from app.models.error import Error
from app.models.id import ID
from app.models.node import Node
from app.models.node_list import NodeList, NodeListWithNodes
from app.models.reduced_info import ReducedInfo

from app.db.tasks import node_create, node_get_all, node_delete, nodelist_create, nodelist_get_by_id, nodelist_get_all, nodelist_delete


class NodeController:

    async def create_node(
        self,
        node: Optional[Node],
    ) -> ID:
        """Create a new node."""
        if not node:
            raise HTTPException(status_code=500, detail="No node provided")
        return node_create(node)


    async def create_node_list(
        self,
        node_list: Optional[NodeList],
    ) -> ID:
        """Create a new node list."""
        if not node_list:
            raise HTTPException(status_code=500, detail="No node list provided")
        return nodelist_create(node_list)


    async def delete_node(
        self,
        nodeId: StrictStr,
    ) -> None:
        """Delete a node."""
        return node_delete(nodeId)


    async def delete_node_list(
        self,
        nodeListId: StrictStr,
    ) -> None:
        """Delete the specified node list."""
        return nodelist_delete(nodeListId)


    async def get_node_list(
        self,
        nodeListId: StrictStr,
    ) -> NodeListWithNodes:
        """Get specified node list."""
        return nodelist_get_by_id(nodeListId)


    async def list_node_lists(
        self,
    ) -> List[ReducedInfo]:
        """List defined node lists."""
        return nodelist_get_all()


    async def list_nodes(
        self,
    ) -> List[Node]:
        """List all available nodes."""
        return node_get_all()
