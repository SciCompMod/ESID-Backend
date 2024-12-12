# coding: utf-8

from typing import ClassVar, Dict, List, Tuple  # noqa: F401
from datetime import date
from pydantic import Field, StrictBytes, StrictFloat, StrictInt, StrictStr
from typing import Any, Dict, List, Optional, Tuple, Union
from typing_extensions import Annotated

from app.models.error import Error
from app.models.id import ID
from app.models.infectiondata import Infectiondata
from app.models.reduced_scenario import ReducedScenario
from app.models.scenario import Scenario
from security_api import get_token_bearerAuth

from app.db.tasks import scenario_create, scenario_get_by_id, scenario_get_all, scenario_delete

class ScenarioController:
    
    async def create_scenario(
        self,
        scenario: Optional[Scenario],
    ) -> ID:
        """Create a new scenario to be simulated."""
        return scenario_create(scenario)


    async def delete_scenario(
        self,
        scenarioId: StrictStr,
    ) -> None:
        """Delete the Scenario and its data"""
        return scenario_delete(scenarioId)

    async def get_scenario(
        self,
        scenarioId: StrictStr,
    ) -> Scenario:
        """Get information about the specified scenario."""
        return scenario_get_by_id(scenarioId)

    async def list_scenarios(
        self,
    ) -> List[ReducedScenario]:
        """List all available scenarios."""
        return scenario_get_all()

    async def get_infection_data(
        self,
        scenarioId: StrictStr,
        nodes: Annotated[Optional[List[StrictStr]], Field(description="Comma separated list of NodeIds or NUTS")],
        start_date: Annotated[Optional[date], Field(description="Start date of requested data")],
        end_date: Annotated[Optional[date], Field(description="End date of requested data")],
        compartments: Annotated[Optional[List[StrictStr]], Field(description="Comma separated list of Compartment IDs")],
        aggregations: Annotated[Optional[Dict[str, Dict[str, List[StrictStr]]]], Field(description="Object with named (key) lists of compartment tags (value, AND connected)")],
        groups: Annotated[Optional[List[StrictStr]], Field(description="List of groups requesting data for")],
        percentiles: Annotated[Optional[List[Union[StrictFloat, StrictInt]]], Field(description="Requested percentiles of the data")],
    ) -> List[Infectiondata]:
        """Get scenario&#39;s infection data based on specified filters."""
        return Infectiondata(values=[]) # TODO Filter Object & DB task

    async def import_scenario_data(
        self,
        scenarioId: StrictStr,
        body: Optional[Union[StrictBytes, StrictStr, Tuple[StrictStr, StrictBytes]]],
    ) -> ID:
        """Supply simulation data for a scenario."""
        # TODO disect file and submit to datapoint_create tasks
        datapoint_create
        return ID(id=scenarioId)

