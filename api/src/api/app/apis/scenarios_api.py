# coding: utf-8

import logging
from typing import List  # noqa: F401
from datetime import date
from pydantic import Field, StrictStr
from typing import List, Optional
from typing_extensions import Annotated
from fastapi import (  # noqa: F401
    APIRouter,
    Body,
    File,
    Path,
    Query,
    Request,
    UploadFile,
)

from app.models.error import Error
from app.models.id import ID
from app.models.infectiondata import Infectiondata
from app.models.reduced_scenario import ReducedScenario
from app.models.scenario import Scenario

from app.controller.scenario_controller import ScenarioController


router = APIRouter()
controller = ScenarioController()

log = logging.getLogger('API.Scenarios')
logging.basicConfig(level=logging.INFO)


@router.post(
    "/scenarios",
    responses={
        201: {"model": ID, "description": "Created new scenario."},
    },
    tags=["Scenarios"],
    response_model_by_alias=True,
)
async def create_scenario(
    request: Request,
    scenario: Scenario = Body(None, description="")
) -> ID:
    """Create a new scenario to be simulated."""

    # Tag creator info
    scenario.creator_user_id = request.state.user.userId if request.state.user else None
    scenario.creator_org_id = request.state.realm if request.state.realm else None
    
    return await controller.create_scenario(
        scenario
    )


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
    scenarioId: StrictStr = Path(..., description="")
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
    scenarioId: StrictStr = Path(..., description="")
) -> Scenario:
    """Get information about the specified scenario."""
    log.info(f'GET /scenarios/{scenarioId} received...')
    log.warning(f'GET /scenarios/{scenarioId} received... [WARN]')
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
    file: UploadFile = File(None, description="zipped HDF5 files of the simulation results")
) -> ID:
    """Supply simulation data for a scenario."""
    log.info(f'PUT /scenarios/{scenarioId} received...')
    return await controller.import_scenario_data(scenarioId, file)


@router.get(
    "/scenarios",
    responses={
        200: {"model": List[ReducedScenario], "description": "Returned list of scenario IDs."},
    },
    tags=["Scenarios"],
    response_model_by_alias=True,
)
async def list_scenarios() -> List[ReducedScenario]:
    """List all available scenarios."""
    return await controller.list_scenarios()

# a toy endpoint to test authorization
@router.post(
    "/auth/test",
    responses={
        200: {"description": "Return authenticated user."},
    },
    tags=["Authentication"],
)
async def return_user(request: Request) -> str:
    """Display authenticated user."""
    return f'Authenticated user: {request.state.user}'

