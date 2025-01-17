# coding: utf-8

from typing import Dict, List  # noqa: F401
from datetime import date
from pydantic import Field, StrictBytes, StrictFloat, StrictInt, StrictStr
from typing import Any, Dict, List, Optional, Tuple, Union
from typing_extensions import Annotated
from fastapi import (  # noqa: F401
    APIRouter,
    Body,
    Cookie,
    Depends,
    File,
    Form,
    Header,
    HTTPException,
    Path,
    Query,
    Response,
    Security,
    status,
    UploadFile,
)

from app.models.extra_models import TokenModel  # noqa: F401
from app.models.error import Error
from app.models.id import ID
from app.models.infectiondata import Infectiondata
from app.models.reduced_scenario import ReducedScenario
from app.models.scenario import Scenario
from security_api import get_token_bearerAuth

from app.controller.scenario_controller import ScenarioController

router = APIRouter()
controller = ScenarioController()


@router.post(
    "/scenarios",
    responses={
        201: {"model": ID, "description": "Created new scenario."},
    },
    tags=["Scenarios"],
    response_model_by_alias=True,
)
async def create_scenario(
    scenario: Scenario = Body(None, description=""),
    token_bearerAuth: TokenModel = Security(
        get_token_bearerAuth
    ),
) -> ID:
    """Create a new scenario to be simulated."""
    return await controller.create_scenario(scenario)


@router.delete(
    "/scenarios/{scenarioId}",
    responses={
        200: {"description": "Deleted scenario."},
        409: {"model": Error, "description": "Preconditions not met. Error contains reason. May have additional properties referenced in error."},
    },
    tags=["Scenarios"],
    response_model_by_alias=True,
)
async def delete_scenario(
    scenarioId: StrictStr = Path(..., description=""),
    token_bearerAuth: TokenModel = Security(
        get_token_bearerAuth
    ),
) -> None:
    """Delete the Scenario and its data"""
    return await controller.delete_scenario(scenarioId)


@router.get(
    "/scenarios/{scenarioId}/infectiondata",
    responses={
        200: {"model": List[Infectiondata], "description": "Returned data matching filters. Unnecessary fields are omitted."},
    },
    tags=["Scenarios"],
    response_model_by_alias=True,
)
async def get_infection_data(
    scenarioId: StrictStr = Path(..., description=""),
    nodes: Annotated[Optional[StrictStr], Field(description="Comma separated list of NodeIds")] = Query(None, description="Comma separated list of NodeIds or NUTS", alias="nodes"),
    start_date: Annotated[Optional[date], Field(description="Start date of requested data")] = Query(None, description="Start date of requested data", alias="startDate"),
    end_date: Annotated[Optional[date], Field(description="End date of requested data")] = Query(None, description="End date of requested data", alias="endDate"),
    compartments: Annotated[Optional[StrictStr], Field(description="Comma separated list of Compartment IDs")] = Query(None, description="Comma separated list of Compartment IDs", alias="compartments"),
    #aggregations: Annotated[Optional[Dict[str, Dict[str, List[StrictStr]]]], Field(description="Object with named (key) lists of compartment tags (value, AND connected)")] = Query(None, description="Object with named (key) lists of compartment tags (value, AND connected)", alias="aggregations"),
    # TODO deepObject not supported by fastapi yet, wait for https://github.com/fastapi/fastapi/pull/9867 or do custom string based solution ¯\_(ツ)_/¯
    groups: Annotated[Optional[StrictStr], Field(description="Comma separated list of groups requesting data for")] = Query(None, description="List of groups requesting data for", alias="groups"),
    percentiles: Annotated[Optional[StrictStr], Field(description="Comma separated list of requested percentiles of the data")] = Query(None, description="Requested percentiles of the data", alias="percentiles"),
    token_bearerAuth: TokenModel = Security(
        get_token_bearerAuth
    ),
) -> List[Infectiondata]:
    """Get scenario&#39;s infection data based on specified filters."""
    return await controller.get_infection_data(scenarioId, nodes, start_date, end_date, compartments, groups, percentiles)


@router.get(
    "/scenarios/{scenarioId}",
    responses={
        200: {"model": Scenario, "description": "Returned scenario."},
    },
    tags=["Scenarios"],
    response_model_by_alias=True,
)
async def get_scenario(
    scenarioId: StrictStr = Path(..., description=""),
    token_bearerAuth: TokenModel = Security(
        get_token_bearerAuth
    ),
) -> Scenario:
    """Get information about the specified scenario."""
    return await controller.get_scenario(scenarioId)


@router.put(
    "/scenarios/{scenarioId}",
    responses={
        201: {"model": ID, "description": "Added data to scenario."},
    },
    tags=["Scenarios"],
    response_model_by_alias=True,
)
async def import_scenario_data(
    scenarioId: StrictStr = Path(..., description="UUID of the scenario"),
    file: UploadFile = File(None, description="zipped HDF5 files of the simulation results"),
    token_bearerAuth: TokenModel = Security(
        get_token_bearerAuth
    ),
) -> ID:
    """Supply simulation data for a scenario."""
    return await controller.import_scenario_data(scenarioId, file)


@router.get(
    "/scenarios",
    responses={
        200: {"model": List[ReducedScenario], "description": "Returned list of scenario IDs."},
    },
    tags=["Scenarios"],
    response_model_by_alias=True,
)
async def list_scenarios(
    token_bearerAuth: TokenModel = Security(
        get_token_bearerAuth
    ),
) -> List[ReducedScenario]:
    """List all available scenarios."""
    return await controller.list_scenarios()
