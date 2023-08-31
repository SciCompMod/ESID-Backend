# coding: utf-8

from __future__ import annotations

import re  # noqa: F401
from datetime import date, datetime  # noqa: F401
from typing import Any, Dict, List, Optional  # noqa: F401

from pydantic import AnyUrl, BaseModel, EmailStr, Field, validator  # noqa: F401


class NodeMigrationsInner(BaseModel):
    """NOTE: This class is auto generated by OpenAPI Generator (https://openapi-generator.tech).

    Do not edit the class manually.

    NodeMigrationsInner - a model defined in OpenAPI

        timestamp: The timestamp of this NodeMigrationsInner [Optional].
        node: The node of this NodeMigrationsInner [Optional].
        incoming: The incoming of this NodeMigrationsInner [Optional].
        outgoing: The outgoing of this NodeMigrationsInner [Optional].
    """

    timestamp: Optional[str] = Field(alias="timestamp", default=None)
    node: Optional[str] = Field(alias="node", default=None)
    incoming: Optional[float] = Field(alias="incoming", default=None)
    outgoing: Optional[float] = Field(alias="outgoing", default=None)


NodeMigrationsInner.update_forward_refs()