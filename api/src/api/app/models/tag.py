# coding: utf-8

from __future__ import annotations
from datetime import date, datetime  # noqa: F401

import re  # noqa: F401
from typing import Any, Dict, List, Optional  # noqa: F401

from pydantic import AnyUrl, BaseModel, EmailStr, Field, validator  # noqa: F401


class Tag(BaseModel):
    """NOTE: This class is auto generated by OpenAPI Generator (https://openapi-generator.tech).

    Do not edit the class manually.

    Tags - a model defined in OpenAPI

        name: The name of this Group [Optional].
        description: The description of this Group [Optional].
        category: The category of this Group [Optional].
        id: The id of this Group.
    """
    name: Optional[str] = Field(alias="name", default=None)
Tag.update_forward_refs()
