# coding: utf-8

from typing import Dict, List, Optional  # noqa: F401

from fastapi import (  # noqa: F401
    APIRouter,
    Body,
    Cookie,
    Depends,
    Form,
    Header,
    Path,
    Query,
    Response,
    Security,
    status,
    UploadFile,
    File,
)

from app.models.extra_models import TokenModel  # noqa: F401
from app.models.id import ID
from app.models.new_scenario import NewScenario
from app.models.scenario import Scenario
from app.models.simulation_run_status import SimulationRunStatus
from security_api import get_token_bearerAuth

from app.controller.simulation_controller import SimulationController

router = APIRouter()
simulation_controller = SimulationController()


@router.post(
    "/scenarios",
    responses={
        200: {"model": ID, "description": "create a new Scenario"},
    },
    tags=["Simulations"],
    response_model_by_alias=True,
)
async def create_simulations(
    new_scenario: NewScenario = Body(None, description=""),
    token_bearerAuth: TokenModel = Security(
        get_token_bearerAuth
    ),
) -> ID:
    return simulation_controller.create_new_scenarios(new_scenario)


@router.delete(
    "/scenarios/{scenario_id}",
    responses={
        202: {"description": "scenario deleted"},
    },
    tags=["Simulations"],
    response_model_by_alias=True,
)
async def delete_scenario(
    scenario_id: str = Path(None, description=""),
    token_bearerAuth: TokenModel = Security(
        get_token_bearerAuth
    ),
) -> None:
    """deletes the Scenario and all its runs"""
    return simulation_controller.delete_scenario_by_id(scenario_id)


@router.delete(
    "/scenarios/{scenario_id}/simulations/{runid}",
    responses={
        202: {"description": "run deleted"},
    },
    tags=["Simulations"],
    response_model_by_alias=True,
)
async def delete_simulation_run(
    scenario_id: str = Path(None, description=""),
    runid: str = Path(None, description=""),
    token_bearerAuth: TokenModel = Security(
        get_token_bearerAuth
    ),
) -> None:
    return simulation_controller.delete_simulations_run_by_id(runid, scenario_id)


@router.get(
    "/scenarios/{scenario_id}/simulations/{runid}/infectiondata",
    responses={
        200: {"model": List[str], "description": "return the account"},
    },
    tags=["Simulations"],
    response_model_by_alias=True,
)
async def get_infection_data(
    scenario_id: str = Path(None, description=""),
    runid: str = Path(None, description=""),
    location: str = Query(None, description=""),
    start_date: str = Query(None, description=""),
    end_date: str = Query(None, description=""),
    compartments: str = Query(None, description=""),
    token_bearerAuth: TokenModel = Security(
        get_token_bearerAuth
    ),
) -> List[str]:
    return simulation_controller.get_infection_data(scenario_id, runid, location, start_date, end_date, compartments)


@router.get(
    "/scenarios/{scenario_id}",
    responses={
        200: {"model": Scenario, "description": "return the account"},
    },
    tags=["Simulations"],
    response_model_by_alias=True,
)
async def get_scenario(
    scenario_id: str = Path(None, description=""),
    token_bearerAuth: TokenModel = Security(
        get_token_bearerAuth
    ),
) -> Scenario:
    return simulation_controller.get_scenario_by_id(scenario_id)


@router.get(
    "/scenarios/{scenario_id}/simulations/{runid}",
    responses={
        200: {"model": SimulationRunStatus, "description": "return the simulation run status"},
    },
    tags=["Simulations"],
    response_model_by_alias=True,
)
async def get_simulation_run_status(
    scenario_id: str = Path(None, description=""),
    runid: str = Path(None, description=""),
    token_bearerAuth: TokenModel = Security(
        get_token_bearerAuth
    ),
) -> SimulationRunStatus:
    return simulation_controller.get_simulation_run_status(scenario_id, runid)


@router.get(
    "/scenarios/{scenario_id}/simulations/{runid}/gridcells",
    responses={
        200: {"model": List[str], "description": "return the account"},
    },
    tags=["Simulations"],
    response_model_by_alias=True,
)
async def list_gridcells(
    scenario_id: str = Path(None, description=""),
    runid: str = Path(None, description=""),
    token_bearerAuth: TokenModel = Security(
        get_token_bearerAuth
    ),
) -> List[str]:
    return simulation_controller.get_gridcells(scenario_id, runid)


@router.get(
    "/scenarios/{scenario_id}/simulations/{runid}/movements",
    responses={
        200: {"model": List[str], "description": "return the account"},
    },
    tags=["Simulations"],
    response_model_by_alias=True,
)
async def list_movments(
    scenario_id: str = Path(None, description=""),
    runid: str = Path(None, description=""),
    token_bearerAuth: TokenModel = Security(
        get_token_bearerAuth
    ),
) -> List[str]:
    return simulation_controller.get_movements(scenario_id, runid)


@router.get(
    "/scenarios",
    responses={
        200: {"model": List[str], "description": "list all Scenarios"},
    },
    tags=["Simulations"],
    response_model_by_alias=True,
)
async def list_scenarios(
    token_bearerAuth: TokenModel = Security(
        get_token_bearerAuth
    ),
) -> List[str]:
    return simulation_controller.get_all_scenarios()


@router.post(
    "/scenarios/{scenario_id}/simulations",
    responses={
        201: {"model": ID, "description": "return the account"},
    },
    tags=["Simulations"],
    response_model_by_alias=True,
)
async def trigger_simulation_run(
    scenario_id: str = Path(None, description=""),
    file: Optional[UploadFile] = File(None, description=""),
    token_bearerAuth: TokenModel = Security(
        get_token_bearerAuth
    ),
) -> ID:
    return await simulation_controller.create_simulations(scenario_id=scenario_id, zip_file=file)
