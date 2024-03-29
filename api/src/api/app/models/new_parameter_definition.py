# coding: utf-8

from __future__ import annotations
from datetime import date, datetime  # noqa: F401

import re  # noqa: F401
from typing import Any, Dict, List, Optional  # noqa: F401

from pydantic import AnyUrl, BaseModel, EmailStr, Field, validator  # noqa: F401


class NewParameterDefinition(BaseModel):
    """NOTE: This class is auto generated by OpenAPI Generator (https://openapi-generator.tech).

    Do not edit the class manually.

    NewParameterDefinition - a model defined in OpenAPI

        name: The name of this NewParameterDefinition [Optional].
        description: The description of this NewParameterDefinition [Optional].
    """

    name: Optional[str] = Field(alias="name", default=None)
    description: Optional[str] = Field(alias="description", default=None)

NewParameterDefinition.update_forward_refs()
