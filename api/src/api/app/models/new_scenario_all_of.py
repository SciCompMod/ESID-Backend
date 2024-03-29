# coding: utf-8

from __future__ import annotations
from datetime import date, datetime  # noqa: F401

import re  # noqa: F401
from typing import Any, Dict, List, Optional  # noqa: F401

from pydantic import AnyUrl, BaseModel, EmailStr, Field, validator  # noqa: F401
from app.models.id import ID
from app.models.parameter_value import ParameterValue


class NewScenarioAllOf(BaseModel):
    """NOTE: This class is auto generated by OpenAPI Generator (https://openapi-generator.tech).

    Do not edit the class manually.

    NewScenarioAllOf - a model defined in OpenAPI

        model_id: The model_id of this NewScenarioAllOf [Optional].
        model_parameters: The model_parameters of this NewScenarioAllOf [Optional].
        node_list_id: The node_list_id of this NewScenarioAllOf [Optional].
        linked_interventions: The linked_interventions of this NewScenarioAllOf [Optional].
    """

    model_id: Optional[str] = Field(alias="modelId", default=None)
    model_parameters: Optional[List[ParameterValue]] = Field(alias="modelParameters", default=None)
    node_list_id: Optional[str] = Field(alias="nodeListId", default=None)
    linked_interventions: Optional[List[ID]] = Field(alias="linkedInterventions", default=None)

NewScenarioAllOf.update_forward_refs()
