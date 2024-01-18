# coding: utf-8

from __future__ import annotations

import re  # noqa: F401
from datetime import date, datetime  # noqa: F401
from typing import Any, Dict, List, Optional  # noqa: F401

from app.models.id import ID
from app.models.parameter_value import ParameterValue
from app.models.scenario_runs_run_id_list_inner import ScenarioRunsRunIdListInner
from pydantic import AnyUrl, BaseModel, EmailStr, Field, validator  # noqa: F401


class Scenario(BaseModel):
    """NOTE: This class is auto generated by OpenAPI Generator (https://openapi-generator.tech).

    Do not edit the class manually.

    Scenario - a model defined in OpenAPI

        id: The id of this Scenario.
        name: The name of this Scenario [Optional].
        description: The description of this Scenario [Optional].
        model_id: The model_id of this Scenario [Optional].
        model_parameters: The model_parameters of this Scenario [Optional].
        node_list_id: The node_list_id of this Scenario [Optional].
        linked_interventions: The linked_interventions of this Scenario [Optional].
    """

    id: str = Field(alias="id")
    name: Optional[str] = Field(alias="name", default=None)
    description: Optional[str] = Field(alias="description", default=None)
    model_id: Optional[str] = Field(alias="modelId", default=None)
    model_parameters: Optional[List[ParameterValue]] = Field(
        alias="modelParameters", default=None
    )
    node_list_id: Optional[str] = Field(alias="nodeListId", default=None)
    linked_interventions: Optional[List[ID]] = Field(
        alias="linkedInterventions", default=None
    )
    run_id_list: Optional[List[ScenarioRunsRunIdListInner]] = Field(
        alias="run_id_list", default=None
    )


Scenario.update_forward_refs()
