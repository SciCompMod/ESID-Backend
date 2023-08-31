import os
import zipfile
from typing import List
from uuid import uuid4

import aiofiles
import pandas as pd
from app.db import tasks
from app.models.gridcell_data import GridcellData
from app.models.id import ID
from app.models.infectiondata import Infectiondata
from app.models.movement_data import MovementData
from app.models.new_scenario import NewScenario
from app.models.node_migrations_inner import NodeMigrationsInner
from app.utils.constants import MigrationSort
from app.utils.utility import _create_empty_directory, _get_input_directory
from fastapi import File, status
from fastapi.exceptions import HTTPException


class SimulationController:
    def create_new_scenarios(self, new_scenerio: NewScenario):
        scenario_id = str(uuid4())
        tasks.create_new_scenario(
            scenario_id,
            new_scenerio.name,
            new_scenerio.description,
            new_scenerio.model_id,
            new_scenerio.node_list_id,
            new_scenerio.linked_interventions,
            new_scenerio.model_parameters,
        )
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

    def _format_movements(self, movements):
        timestamps = [m.timestamp for m in movements]
        cell_movements = {}
        if movements:
            for timestamp in timestamps:
                t_movements = [m for m in movements if m.timestamp == timestamp]
                start_cell_ids = [m.start_cell for m in t_movements]
                end_cell_ids = [m.end_cell for m in t_movements]
                start_cell_ids.extend(end_cell_ids)
                cell_ids = set(start_cell_ids)
                cell_movements[timestamp] = {
                    k: MovementData(
                        incoming=0, outgoing=0, cell=k, timestamp=str(timestamp)
                    )
                    for k in cell_ids
                }
                for movement in t_movements:
                    cell_movements[timestamp][
                        movement.start_cell
                    ].outgoing += movement.value
                    cell_movements[timestamp][
                        movement.end_cell
                    ].incoming += movement.value

        return cell_movements

    def _format_migrations(self, migrations):
        timestamps = [m.timestamp for m in migrations]
        node_migrations = {}
        if migrations:
            for timestamp in timestamps:
                t_migrations = [m for m in migrations if m.timestamp == timestamp]
                start_node_ids = [m.start_node for m in t_migrations]
                end_node_ids = [m.end_node for m in t_migrations]
                start_node_ids.extend(end_node_ids)
                node_ids = set(start_node_ids)
                node_migrations[timestamp] = {
                    k: NodeMigrationsInner(
                        incoming=0, outgoing=0, node=k, timestamp=str(timestamp)
                    )
                    for k in node_ids
                }
                for migration in t_migrations:
                    node_migrations[timestamp][
                        migration.start_node
                    ].outgoing += migration.value
                    node_migrations[timestamp][
                        migration.end_node
                    ].incoming += migration.value

        return node_migrations

    def list_node_migrations(
        self,
        scenario_id: str,
        run_id: str,
        compartment: str,
        start_node: str,
        end_nodes: List[str],
        start_date: str,
        end_date: str,
        aggregation_flag: bool,
        groups: List[str],
    ):
        if aggregation_flag and compartment:
            compartment_objs = tasks.get_compartments_from_aggregation(compartment)
            compartments = [c.name for c in compartment_objs]
        else:
            compartments = [compartment] if compartment else None
        migrations = tasks.get_migrations(
            scenario_id,
            run_id,
            start_node,
            end_nodes,
            start_date,
            end_date,
            compartments,
            groups,
        )
        node_migrations = self._format_migrations(migrations)
        return [v2 for _, v1 in node_migrations.items() for _, v2 in v1.items()]

    def get_top_migrations(
        self,
        scenario_id: str,
        run_id: str,
        compartment: str,
        node: str,
        start_date: str,
        end_date: str,
        aggregation_flag: bool,
        count: int,
        sort: MigrationSort,
        groups: List[str],
    ):
        if aggregation_flag and compartment:
            compartment_objs = tasks.get_compartments_from_aggregation(compartment)
            compartments = [c.name for c in compartment_objs]
        else:
            compartments = [compartment] if compartment else None
        migrations = tasks.get_migrations_for_node(
            scenario_id,
            run_id,
            compartments,
            node,
            start_date,
            end_date,
            groups,
        )
        node_migrations = [
            v2
            for _, v1 in self._format_migrations(migrations).items()
            for _, v2 in v1.items()
        ]
        if node:
            node_migrations = [nm for nm in node_migrations if nm.node == node]

        if sort == MigrationSort.INCOMING:
            node_migrations.sort(key=lambda x: x.incoming, reverse=True)
        elif sort == MigrationSort.OUTGOING:
            node_migrations.sort(key=lambda x: x.outgoing, reverse=True)
        elif sort == MigrationSort.TOTAL:
            node_migrations.sort(key=lambda x: x.incoming + x.outgoing, reverse=True)
        return node_migrations[:count]

    def list_gridcell_data(
        self,
        scenario_id: str,
        run_id: str,
        cells: str,
        start_date: str,
        end_date: str,
        compartment: str,
        aggregation_flag: bool,
        groups: List[str],
        movement_filter: str,
        travel_mode: List[str],
        activity: List[str],
        min_travel_time: str,
        max_travel_time: str,
    ):
        if aggregation_flag and compartment:
            compartment_objs = tasks.get_compartments_from_aggregation(compartment)
            compartments = [c.name for c in compartment_objs]
        else:
            compartments = [compartment] if compartment else None
        movements = tasks.get_all_movements_for_cell(
            scenario_id,
            run_id,
            cells,
            start_date,
            end_date,
            compartments,
            groups,
            movement_filter,
            travel_mode,
            activity,
            min_travel_time,
            max_travel_time,
        )
        cell_movements = [
            v2
            for _, v1 in self._format_movements(movements).items()
            for _, v2 in v1.items()
        ]
        if cells:
            cell_movements = [cm for cm in cell_movements if cm.cell in cells]

        gridcell_data = [
            GridcellData(
                timestamp=x.timestamp, cell=x.cell, value=x.incoming + x.outgoing
            )
            for x in cell_movements
        ]
        return gridcell_data

    def list_cell_movements(
        self,
        scenario_id: str,
        run_id: str,
        cells: str,
        start_date: str,
        end_date: str,
        compartment: str,
        aggregation_flag: bool,
        groups: List[str],
        movement_filter: str,
        travel_mode: List[str],
        activity: List[str],
        min_travel_time: str,
        max_travel_time: str,
    ):
        if aggregation_flag and compartment:
            compartment_objs = tasks.get_compartments_from_aggregation(compartment)
            compartments = [c.name for c in compartment_objs]
        else:
            compartments = [compartment] if compartment else None
        movements = tasks.get_all_movements_for_cell(
            scenario_id,
            run_id,
            cells,
            start_date,
            end_date,
            compartments,
            groups,
            movement_filter,
            travel_mode,
            activity,
            min_travel_time,
            max_travel_time,
        )
        cell_movements = [
            v2
            for _, v1 in self._format_movements(movements).items()
            for _, v2 in v1.items()
        ]
        if cells:
            cell_movements = [cm for cm in cell_movements if cm.cell in cells]
        return cell_movements

    def get_infection_data(
        self, scenario_id, runid, location, start_date, end_date, compartments
    ):
        if tasks.check_scenario(scenario_id, runid):
            return [str(uuid4())]
        else:
            {"message": f"Scenario with id: {scenario_id} not found!", "status": 404}

    def get_gridcells(self, scenario_id, runid):
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
            async with aiofiles.open(filepath, "wb") as out_file:
                content = await file.read()
                await out_file.write(content)
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="There was an error uploading the file",
            )
        finally:
            await file.close()

        output_folder = os.path.join(input_directory, "extracted")
        with zipfile.ZipFile(filepath, "r") as zip_ref:
            zip_ref.extractall(output_folder)

        csv_paths = []
        for csv_file in os.listdir(output_folder):
            if csv_file.endswith(".csv"):
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
                if all(elem in df.columns for elem in req_columns):
                    infection_rows = df.to_dict("records")
                    tasks.create_multiple_infectiondata_from_dicts(infection_rows)
                else:
                    raise Exception(
                        f"The csv files do not contain required columns:{req_columns}"
                    )

        tasks.create_run_simulations(run_id=run_id, scenario_id=scenario_id)
        return ID(id=run_id)

    def delete_simulations_run_by_id(self, run_id, scenario_id):
        tasks.delete_simulations_run_by_id(run_id)
        return {"message": f"Scenario with id: {run_id} deleted"}
