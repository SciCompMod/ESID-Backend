# coding: utf-8

from typing import ClassVar, Dict, List, Tuple  # noqa: F401
from pydantic import StrictStr
from typing import Any, List, Optional
from fastapi import HTTPException

from app.models.error import Error
from app.models.group import Group
from app.models.id import ID
from security_api import get_token_bearerAuth

from app.db.tasks import group_create, group_delete_by_id, group_get_all, group_get_all_categories


class GroupsController:
    async def create(
            self,
            group: Optional[Group]
    ) -> ID:
        """Create a new (stratification) group. All groups with the same category are mutually exclusive."""
        if not group:
            raise HTTPException(status_code=500, detail="No group provided")
        return group_create(group)
    
    async def delete(
            self,
            groupId: StrictStr
    ) -> None:
        """Delete the specified group."""
        return group_delete_by_id(groupId)


    async def getAll(
            self
        ) -> List[ID]:
        """List all (stratification) groups."""
        return group_get_all()

    async def getCategories(
            self
    ) -> List[str]:
        """List all existing categories."""
        return group_get_all_categories()