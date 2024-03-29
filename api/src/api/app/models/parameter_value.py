# coding: utf-8

from __future__ import annotations
from datetime import date, datetime  # noqa: F401

import re  # noqa: F401
from typing import Any, Dict, List, Optional  # noqa: F401

from pydantic import AnyUrl, BaseModel, EmailStr, Field, validator  # noqa: F401
from app.models.parameter_value_range import ParameterValueRange


class ParameterValue(BaseModel):
    """NOTE: This class is auto generated by OpenAPI Generator (https://openapi-generator.tech).

    Do not edit the class manually.

    ParameterValue - a model defined in OpenAPI

        parameter_id: The parameter_id of this ParameterValue.
        groups: The groups of this ParameterValue [Optional].
        categories: The categories of this ParameterValue [Optional].
    """

    parameter_id: str = Field(alias="parameterId")
    groups: Optional[List[ParameterValueRange]] = Field(alias="groups", default=None)
    categories: Optional[List[ParameterValueRange]] = Field(alias="categories", default=None)

ParameterValue.update_forward_refs()
