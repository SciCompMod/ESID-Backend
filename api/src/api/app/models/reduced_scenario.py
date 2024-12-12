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




from datetime import date
from pydantic import BaseModel, ConfigDict, Field, StrictStr
from typing import Any, ClassVar, Dict, List, Optional
try:
    from typing import Self
except ImportError:
    from typing_extensions import Self

class ReducedScenario(BaseModel):
    """
    ReducedScenario
    """ # noqa: E501
    id: StrictStr
    name: StrictStr = Field(description="Display Name of the object")
    description: Optional[StrictStr] = Field(default=None, description="(Tooltip) Description of the object")
    start_date: Optional[date] = Field(default=None, alias="startDate")
    end_date: Optional[date] = Field(default=None, alias="endDate")
    __properties: ClassVar[List[str]] = ["id", "name", "description", "startDate", "endDate"]

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
        """Create an instance of ReducedScenario from a JSON string"""
        return cls.from_dict(json.loads(json_str))

    def to_dict(self) -> Dict[str, Any]:
        """Return the dictionary representation of the model using alias.

        This has the following differences from calling pydantic's
        `self.model_dump(by_alias=True)`:

        * `None` is only added to the output dict for nullable fields that
          were set at model initialization. Other fields with value `None`
          are ignored.
        * OpenAPI `readOnly` fields are excluded.
        """
        _dict = self.model_dump(
            by_alias=True,
            exclude={
                "id",
            },
            exclude_none=True,
        )
        return _dict

    @classmethod
    def from_dict(cls, obj: Dict) -> Self:
        """Create an instance of ReducedScenario from a dict"""
        if obj is None:
            return None

        if not isinstance(obj, dict):
            return cls.model_validate(obj)

        _obj = cls.model_validate({
            "id": obj.get("id"),
            "name": obj.get("name"),
            "description": obj.get("description"),
            "startDate": obj.get("startDate"),
            "endDate": obj.get("endDate")
        })
        return _obj


