# coding: utf-8

"""
    Pandemos

    API for visualization of Infection Models

    The version of the OpenAPI document: 1
    Generated by OpenAPI Generator (https://openapi-generator.tech)

    Do not edit the class manually.
"""  # noqa: E501


from __future__ import annotations
import pprint
import re  # noqa: F401
import json




from datetime import date, datetime
import uuid
from pydantic import BaseModel, ConfigDict, Field, StrictStr
from typing import Any, ClassVar, Dict, List, Optional
from app.models.intervention_implementation import InterventionImplementation
from app.models.parameter_value import ParameterValue
try:
    from typing import Self
except ImportError:
    from typing_extensions import Self

class Scenario(BaseModel):
    """
    Scenario
    """ # noqa: E501
    id: Optional[StrictStr] = Field(default_factory=uuid.uuid4)
    name: StrictStr = Field(description="Display Name of the object")
    description: Optional[StrictStr] = Field(default=None, description="(Tooltip) Description of the object")
    start_date: date = Field(alias="startDate")
    end_date: date = Field(alias="endDate")
    model_id: StrictStr = Field(description="UUID of the model this scenario belongs to", alias="modelId")
    model_parameters: List[ParameterValue] = Field(description="List of (available) model parameters (UUIDs & values)", alias="modelParameters")
    node_list_id: StrictStr = Field(description="UUID of the node list (districts etc.) of this scenario", alias="nodeListId")
    linked_interventions: Optional[List[InterventionImplementation]] = Field(default=None, description="List of intervention implementations used in this scenario", alias="linkedInterventions")
    timestamp_submitted: Optional[datetime] = Field(default=None, alias="timestampSubmitted")
    timestamp_simulated: Optional[datetime] = Field(default=None, alias="timestampSimulated")
    __properties: ClassVar[List[str]] = ["id", "name", "description", "startDate", "endDate", "modelId", "modelParameters", "nodeListId", "linkedInterventions", "timestampSubmitted", "timestampSimulated"]

    model_config = {
        "populate_by_name": True,
        "validate_assignment": True,
        "protected_namespaces": (),
    }


    def to_str(self) -> str:
        """Returns the string representation of the model using alias"""
        return pprint.pformat(self.model_dump(by_alias=True))

    def to_json(self) -> str:
        """Returns the JSON representation of the model using alias"""
        # TODO: pydantic v2: use .model_dump_json(by_alias=True, exclude_unset=True) instead
        return json.dumps(self.to_dict())

    @classmethod
    def from_json(cls, json_str: str) -> Self:
        """Create an instance of Scenario from a JSON string"""
        return cls.from_dict(json.loads(json_str))

    def to_dict(self) -> Dict[str, Any]:
        """Return the dictionary representation of the model using alias.

        This has the following differences from calling pydantic's
        `self.model_dump(by_alias=True)`:

        * `None` is only added to the output dict for nullable fields that
          were set at model initialization. Other fields with value `None`
          are ignored.
        * OpenAPI `readOnly` fields are excluded.
        * OpenAPI `readOnly` fields are excluded.
        * OpenAPI `readOnly` fields are excluded.
        """
        _dict = self.model_dump(
            by_alias=True,
            exclude={
                "id",
                "timestamp_submitted",
                "timestamp_simulated",
            },
            exclude_none=True,
        )
        # override the default output from pydantic by calling `to_dict()` of each item in model_parameters (list)
        _items = []
        if self.model_parameters:
            for _item in self.model_parameters:
                if _item:
                    _items.append(_item.to_dict())
            _dict['modelParameters'] = _items
        # override the default output from pydantic by calling `to_dict()` of each item in linked_interventions (list)
        _items = []
        if self.linked_interventions:
            for _item in self.linked_interventions:
                if _item:
                    _items.append(_item.to_dict())
            _dict['linkedInterventions'] = _items
        return _dict

    @classmethod
    def from_dict(cls, obj: Dict) -> Self:
        """Create an instance of Scenario from a dict"""
        if obj is None:
            return None

        if not isinstance(obj, dict):
            return cls.model_validate(obj)

        _obj = cls.model_validate({
            "id": obj.get("id"),
            "name": obj.get("name"),
            "description": obj.get("description"),
            "startDate": obj.get("startDate"),
            "endDate": obj.get("endDate"),
            "modelId": obj.get("modelId"),
            "modelParameters": [ParameterValue.from_dict(_item) for _item in obj.get("modelParameters")] if obj.get("modelParameters") is not None else None,
            "nodeListId": obj.get("nodeListId"),
            "linkedInterventions": [InterventionImplementation.from_dict(_item) for _item in obj.get("linkedInterventions")] if obj.get("linkedInterventions") is not None else None,
            "timestampSubmitted": obj.get("timestampSubmitted"),
            "timestampSimulated": obj.get("timestampSimulated")
        })
        return _obj
