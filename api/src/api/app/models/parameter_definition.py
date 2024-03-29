# coding: utf-8

from __future__ import annotations
from datetime import date, datetime  # noqa: F401

import re  # noqa: F401
from typing import Any, Dict, List, Optional  # noqa: F401

from pydantic import AnyUrl, BaseModel, EmailStr, Field, validator  # noqa: F401


class ParameterDefinition(BaseModel):
    """NOTE: This class is auto generated by OpenAPI Generator (https://openapi-generator.tech).

    Do not edit the class manually.

    ParameterDefinition - a model defined in OpenAPI

        name: The name of this ParameterDefinition [Optional].
        description: The description of this ParameterDefinition [Optional].
        id: The id of this ParameterDefinition.
    """

    name: Optional[str] = Field(alias="name", default=None)
    description: Optional[str] = Field(alias="description", default=None)
    id: str = Field(alias="id")

ParameterDefinition.update_forward_refs()
