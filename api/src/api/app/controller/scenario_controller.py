# coding: utf-8

from typing import ClassVar, Dict, List, Tuple  # noqa: F401
from datetime import date, timedelta
import zipfile
import aiofiles
import asyncio
import h5py
from pathlib import Path
from pydantic import Field, StrictBytes, StrictFloat, StrictInt, StrictStr
from typing import Any, Dict, List, Optional, Tuple, Union
from typing_extensions import Annotated
from fastapi import HTTPException, UploadFile
import os
import re

from app.utils.utility import _get_input_directory, _create_empty_directory

from app.models.error import Error
from app.models.id import ID
from app.models.infectiondata import Infectiondata
from app.models.reduced_scenario import ReducedScenario
from app.models.scenario import Scenario
from app.models.model import Model
from app.models.group import Group
from app.models.compartment import Compartment
from app.models.node_list import NodeList
from app.models.node import Node
from security_api import get_token_bearerAuth

from app.db.tasks import (
    scenario_create,
    scenario_get_by_id,
    scenario_get_all,
    scenario_get_data_by_filter,
    scenario_delete,
    model_get_by_id,
    group_get_all,
    compartment_get_all,
    node_get_by_list,
    datapoint_create_batch
)

class LookupObject:
    scenario: Scenario = None
    model: Model = None
    groups: List[Group] = []
    compartments: List[Compartment] = []
    nodes: List[Node]

CompartmentNames = {
    0: "MildInfections",
    1: "Hospitalized",
    2: "ICU",
    3: "Dead"
}

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
        file: UploadFile,
    ) -> ID:
        """Supply simulation data for a scenario."""
        if not file or not file.filename.endswith('.zip'):
            raise HTTPException(
                status_code=422,
                detail="No file uploaded with request or not a .zip file"
            )
        percentile_paths = await self._read_zip_file(file)
        
        # Get info for lookups
        info = LookupObject()
        info.scenario = scenario_get_by_id(scenarioId)
        info.model = model_get_by_id(info.scenario.model_id)
        info.groups = [group for group in group_get_all() if group.id in info.model.groups]
        info.compartments = [comp for comp in compartment_get_all() if comp.id in info.model.compartments]
        info.nodes = node_get_by_list(info.scenario.node_list_id)
        # Handle h5 files for each percentile asynchronously
        res = await asyncio.gather(*[self._read_percentiles(perc, percentile_paths[perc], info) for perc in percentile_paths.keys()], return_exceptions=True)
        print(res)
        # Check if any percs had errors
        errors = [ex for ex in res if ex != None]
        if errors:
            message = {}
            for error in errors:
                message = error.args
            raise HTTPException(
                status_code=422,
                detail=message
            )
        return ID(id=scenarioId)


    async def _read_zip_file(
        self,
        file: UploadFile,
    ) -> Dict[int, str]:
        """
        A helper function to read the zip file asynchronously and save it in the input directory for further processing.
        Args:
            file (File): zip-file to be read
        """
        try:
            zip_fname: str = file.filename
            fname: str = zip_fname.replace('.zip', '')
            input_dir: str = os.path.join(_get_input_directory(), fname)
            _create_empty_directory(input_dir)
            fpath: str = os.path.join(input_dir, zip_fname)
            # Write uploaded file into input dir
            async with aiofiles.open(fpath, "wb") as out_file:
                content = await file.read()
                await out_file.write(content)
        except Exception:
            raise HTTPException(status_code=500, detail='There was an error uploading the file')
        finally:
            await file.close()
        # Unzip file
        out_folder: str = os.path.join(input_dir, "extracted")
        with zipfile.ZipFile(fpath, 'r') as zip_ref:
            zip_ref.extractall(out_folder)
        
        # Record uploaded percentiles and their paths
        percentile_paths: Dict[int, str] = {}
        expr = re.compile(r'^p([0-9]{1,2})$')

        for percentile_dir in os.listdir(out_folder):
            # validate percentile folders or raise exception
            result = expr.match(percentile_dir)
            if not result:
                raise HTTPException(
                    status_code=422,
                    detail='The zip file internal folder structure of results does not match expected format'
                )
            percentile_paths[int(result.group(1))] = os.path.join(out_folder, percentile_dir)

        return percentile_paths
    

    async def _read_percentiles(
            self,
            percentile: int,
            path: str,
            infos: LookupObject
    ) -> None:
        """
        A helper function to read the h5 files of a percentile asynchronously and send it to the DB.
        Args:
            percentile (int): value of the percentile
            path (str): path in the input dir to the folder with the h5 files
        """
        # Get h5-files from folder
        h5_files = list(Path(path).glob('*.h5'))
        datapoints: List[Infectiondata] = []

        for path in h5_files:
            is_validated = False
            # validate nodes
            file = h5py.File(path, "r")
            for node in file.keys():
                for group in file[node].keys():
                    if(group == 'Time'):
                        # Skip Time group
                        continue
                    for dayoffset, compartments in enumerate(file[node][group]):
                        for compartment, value in enumerate(compartments):
                            # Create Datapoint from infos
                            datapoints.append(Infectiondata(
                                date=infos.scenario.start_date + timedelta(days=dayoffset),
                                node=next((n.id for n in infos.nodes if n.nuts == node.zfill(6)), node.zfill(6)),
                                group=next((g.id for g in infos.groups if g.name == group), group),
                                compartment=next((c for c in infos.compartments if c.name == CompartmentNames[compartment]), CompartmentNames[compartment]),
                                percentile=percentile,
                                value=value
                            ))
        datapoint_create_batch(infos.scenario.id , datapoints)
        return