# coding: utf-8

from typing import ClassVar, Dict, List, Tuple  # noqa: F401
from pydantic import StrictStr
from typing import Any, List, Optional

from app.models.error import Error
from app.models.id import ID
from app.models.parameter_definition import ParameterDefinition
from security_api import get_token_bearerAuth

from app.db.tasks import parameter_definition_create, parameter_definition_get_all, parameter_definition_delete

class ParameterController:
    
    async def create_parameter_definition(
        self,
        parameter_definition: Optional[ParameterDefinition],
    ) -> ID:
        """Create a new parameter definition."""
        return parameter_definition_create(parameter_definition)


    async def delete_parameter_definition(
        self,
        parameterId: StrictStr,
    ) -> None:
        """Delete a parameter definition."""
        return parameter_definition_delete(parameterId)


    async def list_parameter_definitions(
        self,
    ) -> List[ParameterDefinition]:
        """List all existing Parameter definitions."""
        return parameter_definition_get_all()
