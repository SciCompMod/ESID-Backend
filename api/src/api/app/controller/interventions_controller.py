# coding: utf-8

from typing import ClassVar, Dict, List, Tuple  # noqa: F401
from pydantic import StrictStr
from typing import Any, List, Optional
from fastapi import HTTPException

from app.models.error import Error
from app.models.id import ID
from app.models.intervention_template import InterventionTemplate

from app.db.tasks import intervention_template_create, intervention_template_delete, intervention_template_get_all

class InterventionsController:
    async def create_intervention_template(
        self,
        intervention_template: Optional[InterventionTemplate],
    ) -> ID:
        """Creates a new intervention template to be used in implementations."""
        if not intervention_template:
            raise HTTPException(status_code=500, detail="No intervention template provided")
        return intervention_template_create(intervention_template)


    async def delete_intervention_template(
        self,
        interventionTemplateId: StrictStr,
    ) -> None:
        """Delete an intervention template."""
        return intervention_template_delete(interventionTemplateId)


    async def list_intervention_templates(
        self,
    ) -> List[InterventionTemplate]:
        """List available Intervention templates that can be implemented."""
        return intervention_template_get_all()
