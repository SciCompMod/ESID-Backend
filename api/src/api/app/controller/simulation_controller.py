from app.models.new_scenario import NewScenario
from app.models.scenario import Scenario
from app.models.infectiondata import Infectiondata
from app.models.id import ID
from app.db import tasks
from uuid import uuid4

import zipfile
from fastapi import File, status
from fastapi.exceptions import HTTPException
from app.utils.utility import _get_input_directory, _create_empty_directory, _create_directory
import os
import aiofiles
import pandas as pd


class SimulationController:
    def create_new_scenarios(self, new_scenerio: NewScenario):
        scenario_id = str(uuid4())
        tasks.create_new_scenario(scenario_id, new_scenerio.name, new_scenerio.description, new_scenerio.model_id,
                                  new_scenerio.node_list_id, new_scenerio.linked_interventions, new_scenerio.model_parameters)
        return ID(id=scenario_id)

    def get_all_scenarios(self):
        scenarios = tasks.get_all_scenarios()
        scenario_ids = []
        if scenarios:
            scenario_ids = [scenario.id for scenario in scenarios]
        return scenario_ids

    def get_scenario_by_id(self, scenario_id):
        scenario = tasks.get_scenario_by_id(scenario_id)
        return scenario

    def delete_scenario_by_id(self, scenario_id):
        tasks.delete_scenario_by_id(scenario_id)
        return {"message": f"Scenario with id: {scenario_id} deleted"}

    def get_simulation_run_status(self, scenario_id, runid):
        if tasks.check_scenario(scenario_id, runid):
            return {"TRIGGERED"}
        else:
            {"message": f"Scenario with id: {scenario_id} not found!", "status": 404}

    def get_infection_data(self, scenario_id, runid, location, start_date, end_date, compartments):
        if tasks.check_scenario(scenario_id, runid):
            return [str(uuid4())]
        else:
            {"message": f"Scenario with id: {scenario_id} not found!", "status": 404}

    def get_gridcells(self, scenario_id, runid):
        if tasks.check_scenario(scenario_id):
            return [str(uuid4())]
        else:
            {"message": f"Scenario with id: {scenario_id} not found!", "status": 404}

    def get_movements(self, scenario_id, runid):
        if tasks.check_scenario(scenario_id):
            return [str(uuid4())]
        else:
            {"message": f"Scenario with id: {scenario_id} not found!", "status": 404}

    async def _read_zip_file(self, file: File):
        """A helper function to read the pdf file asynchronously
        and save it in the input directory for further processing
        Args:
            file (File): file to be read
        """
        try:
            zip_filename = file.filename
            fname = zip_filename.replace(".zip", "")
            input_directory = os.path.join(_get_input_directory(), fname)
            _create_empty_directory(input_directory)
            filepath = os.path.join(input_directory, zip_filename)
            print(filepath)
            async with aiofiles.open(
                filepath, "wb"
            ) as out_file:
                content = await file.read()
                await out_file.write(content)
        except Exception:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
                detail='There was an error uploading the file')
        finally:
            await file.close()

        output_folder = os.path.join(input_directory, "extracted")
        with zipfile.ZipFile(filepath, 'r') as zip_ref:
            zip_ref.extractall(output_folder)
        
        csv_paths = []
        for csv_file in os.listdir(output_folder):
            if csv_file.endswith('.csv'):
                csv_path = os.path.join(output_folder, csv_file)
                csv_paths.append(csv_path)
        return csv_paths


    async def create_simulations(self, scenario_id, zip_file):
        run_id = str(uuid4())
        if zip_file is not None:
            req_columns = Infectiondata().dict().keys()
            csv_paths = await self._read_zip_file(zip_file)
            for csv_path in csv_paths:
                df = pd.read_csv(csv_path)
                if all(elem in df.columns  for elem in req_columns):
                    infection_rows = df.to_dict('records')
                    tasks.create_multiple_infectiondata_from_dicts(infection_rows)
                else:
                    raise Exception(f"The csv files do not contain required columns:{req_columns}")
                
        tasks.create_run_simulations(run_id=run_id, scenario_id=scenario_id)
        return ID(id=run_id)

    def delete_simulations_run_by_id(self, run_id, scenario_id):
        tasks.delete_simulations_run_by_id(run_id)
        return {"message": f"Scenario with id: {run_id} deleted"}
