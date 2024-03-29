# coding: utf-8

from __future__ import annotations
from datetime import date, datetime  # noqa: F401

import re  # noqa: F401
from typing import Any, Dict, List, Optional  # noqa: F401

from pydantic import AnyUrl, BaseModel, EmailStr, Field, validator  # noqa: F401
from app.models.id import ID
from app.models.parameter_value import ParameterValue


class NewScenario(BaseModel):
    """NOTE: This class is auto generated by OpenAPI Generator (https://openapi-generator.tech).

    Do not edit the class manually.

    NewScenario - a model defined in OpenAPI

        name: The name of this NewScenario [Optional].
        description: The description of this NewScenario [Optional].
        model_id: The model_id of this NewScenario [Optional].
        model_parameters: The model_parameters of this NewScenario [Optional].
        node_list_id: The node_list_id of this NewScenario [Optional].
        linked_interventions: The linked_interventions of this NewScenario [Optional].
    """

    name: Optional[str] = Field(alias="name", default=None)
    description: Optional[str] = Field(alias="description", default=None)
    model_id: Optional[str] = Field(alias="modelId", default=None)
    model_parameters: Optional[List[ParameterValue]] = Field(alias="modelParameters", default=None)
    node_list_id: Optional[str] = Field(alias="nodeListId", default=None)
    linked_interventions: Optional[List[ID]] = Field(alias="linkedInterventions", default=None)

NewScenario.update_forward_refs()
