# coding: utf-8

from __future__ import annotations
from datetime import date, datetime  # noqa: F401

import re  # noqa: F401
from typing import Any, Dict, List, Optional  # noqa: F401

from pydantic import AnyUrl, BaseModel, EmailStr, Field, validator  # noqa: F401


class NodeList(BaseModel):
    """NOTE: This class is auto generated by OpenAPI Generator (https://openapi-generator.tech).

    Do not edit the class manually.

    NodeList - a model defined in OpenAPI

        name: The name of this NodeList [Optional].
        description: The description of this NodeList [Optional].
        node_ids: The node_ids of this NodeList [Optional].
        id: The id of this NodeList.
    """

    name: Optional[str] = Field(alias="name", default=None)
    description: Optional[str] = Field(alias="description", default=None)
    node_ids: Optional[List[List]] = Field(alias="nodeIds", default=None)
    id: str = Field(alias="id")

NodeList.update_forward_refs()
