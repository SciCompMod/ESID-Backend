# coding: utf-8

from typing import ClassVar, Dict, List, Tuple  # noqa: F401
from pydantic import StrictStr
from typing import Any, List, Optional
from fastapi import HTTPException

from app.models.error import Error
from app.models.compartment import Compartment
from app.models.id import ID
from security_api import get_token_bearerAuth

from app.db.tasks import compartment_create, compartment_delete, compartment_get_all


class CompartmentController:
    
    async def create_compartment(
        self,
        compartment: Optional[Compartment],
    ) -> ID:
        """Create a new compartment."""
        if not compartment:
            raise HTTPException(status_code=500, detail="No compartment provided")
        return compartment_create(compartment)


    async def delete_compartment(
        self,
        compartmentId: StrictStr,
    ) -> None:
        """Delete specific compartment."""
        return compartment_delete(compartmentId)


    async def list_compartments(
        self,
    ) -> List[Compartment]:
        """List all existing compartments."""
        return compartment_get_all()
