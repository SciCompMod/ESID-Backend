# coding: utf-8

from typing import ClassVar, Dict, List, Tuple  # noqa: F401
from datetime import date
from pydantic import Field, StrictBytes, StrictFloat, StrictInt, StrictStr
from typing import Any, Dict, List, Optional, Tuple, Union
from typing_extensions import Annotated
from fastapi import HTTPException

from app.models.error import Error
from app.models.id import ID
from app.models.infectiondata import Infectiondata
from app.models.reduced_scenario import ReducedScenario
from app.models.scenario import Scenario
from security_api import get_token_bearerAuth

from app.db.tasks import scenario_create, scenario_get_by_id, scenario_get_all, scenario_get_data_by_filter, scenario_delete

class ScenarioController:
    
    async def create_scenario(
        self,
        scenario: Optional[Scenario],
    ) -> ID:
        """Create a new scenario to be simulated."""
        if not scenario:
            raise HTTPException(status_code=500, detail="No scenario provided")
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
        nodes: Optional[StrictStr],
        start_date: Optional[date],
        end_date: Optional[date],
        compartments: Optional[StrictStr],
        # aggregations: Optional[Dict[str, Dict[str, List[StrictStr]]]],
        groups: Optional[StrictStr],
        percentiles: Optional[StrictStr],
    ) -> List[Infectiondata]:
        """Get scenario&#39;s infection data based on specified filters."""
        return scenario_get_data_by_filter(
            scenarioId=scenarioId,
            nodes=[StrictStr(node) for node in nodes.split(',')] if nodes else None,
            start_date=start_date,
            end_date=end_date,
            compartments=[StrictStr(comp) for comp in compartments.split(',')] if compartments else None,
            # aggregations,
            groups=[StrictStr(group) for group in groups.split(',')] if groups else None,
            percentiles=[StrictInt(perc) for perc in percentiles.split(',')] if percentiles else [StrictInt(50)]
        )

    async def import_scenario_data(
        self,
        scenarioId: StrictStr,
        body: Optional[Union[StrictBytes, StrictStr, Tuple[StrictStr, StrictBytes]]],
    ) -> ID:
        """Supply simulation data for a scenario."""
        # TODO disect file and submit to datapoint_create tasks
        return ID(id=scenarioId)

