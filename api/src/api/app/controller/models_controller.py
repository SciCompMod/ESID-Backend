# coding: utf-8

from typing import ClassVar, Dict, List, Tuple  # noqa: F401
from pydantic import StrictStr
from typing import Any, List, Optional
from fastapi import HTTPException

from app.models.error import Error
from app.models.id import ID
from app.models.model import Model
from app.models.reduced_info import ReducedInfo
from security_api import get_token_bearerAuth

from app.db.tasks import model_create, model_delete, model_get_by_id, model_get_all


class ModelController:

    async def create_model(
        self,
        model: Optional[Model],
    ) -> ID:
        """Create a new simulation model."""
        if not model:
            raise HTTPException(status_code=500, detail="No model provided")
        return model_create(model)


    async def delete_model(
        self,
        modelId: StrictStr,
    ) -> None:
        """Delete a model if it is not referenced in any scenarios."""
        return model_delete(modelId)


    async def get_model(
        self,
        modelId: StrictStr,
    ) -> Model:
        """Get specific model information."""
        return model_get_by_id(modelId)


    async def list_models(
        self,
    ) -> List[ReducedInfo]:
        """List all available simulation models."""
        return model_get_all()
