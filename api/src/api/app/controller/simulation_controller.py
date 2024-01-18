import json
import os
import zipfile
from typing import List
from uuid import uuid4
from datetime import datetime, timedelta

import aiofiles
import h5py
import pandas as pd
from app.db import tasks
from app.models.gridcell_data import GridcellData
from app.models.id import ID
from app.models.movement_data import MovementData
from app.models.new_scenario import NewScenario
from app.models.node_migrations_inner import NodeMigrationsInner
from app.utils.constants import MigrationSort
from app.utils.utility import _create_empty_directory, _get_input_directory
from fastapi import File, status
from fastapi.exceptions import HTTPException
from app.models.infectiondata import Infectiondata


class SimulationController:
    def create_new_scenarios(self, new_scenario: NewScenario):
        scenario_id = str(uuid4())
        tasks.create_new_scenario(
            scenario_id,
            new_scenario.name,
            new_scenario.description,
            new_scenario.model_id,
            new_scenario.node_list_id,
            new_scenario.linked_interventions,
            new_scenario.model_parameters,
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
        self, scenario_id, runid, node, start_date, end_date, compartments, groups
    ):
        if tasks.check_scenario(scenario_id, runid):
            infection_data_list = []      
            # change start and end date to to datetime format and calculate the toal days between them
            formatted_start_date = datetime.strptime(start_date, "%Y-%m-%d")
            total_days = (datetime.strptime(end_date, "%Y-%m-%d") - formatted_start_date).days + 1
            
            for day in range(total_days):
                infected_values = []
                # get the range of date from start to end date
                timestamp = str((formatted_start_date + timedelta(days=day)).timestamp())
                # get infection data for list of groups in a node
                for group in groups:
                    infection_data = tasks.get_infection_data(timestamp, node, group)
                    for data in infection_data:
                        # get the value of the specified compartment
                        infected_values.append(data.dict()[compartments])


                total_value = sum(infected_values)
                total_value = f"{total_value:.2f}"
                # create the infection data object
                infection_data_obj = Infectiondata(timestamp=timestamp, node=node, value=total_value)
                infection_data_list.append(infection_data_obj)
            return infection_data_list
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

        h5_paths = []
        for h5_file in os.listdir(os.path.join(output_folder, fname)):
            if h5_file.endswith(".h5"):
                h5_path = os.path.join(output_folder, fname, h5_file)
                h5_paths.append(h5_path)
        return h5_paths, os.path.join(output_folder, fname, "metadata.json")

    async def create_simulations(self, scenario_id, zip_file):
        run_id = str(uuid4())
        if zip_file is not None:
            h5_paths, metadata_path = await self._read_zip_file(zip_file)
            metadata = json.load(open(metadata_path))
            start_date = metadata["startDay"]
            tasks.create_groups(metadata["groupMapping"])
            formatted_date = datetime.strptime(start_date, "%Y-%m-%d")
            scenario_timestamp = datetime.strptime(start_date, "%Y-%m-%d").timestamp()
            h5_paths = [x for x in h5_paths if "sum" not in x]
            for h5_path in h5_paths:
                h_file = h5py.File(h5_path, "r")

                rows = []
                for node in h_file.keys():
                    tasks.create_nodes(node)
                    groups = list(h_file[node].keys())
                    groups.remove("Time")
                    groups.remove("Total")
                    for group in groups:
                        values = h_file[node][group][()]
                        for i in range(len(values)):
                            group_date = str((formatted_date + timedelta(days=i)).timestamp())
                            values_list = list(values[i])
                            if len(node) != 5:
                                new_node = "0" + node
                            else:
                                new_node = node

                            rows.append(
                                {
                                    "node": new_node,
                                    "group": group,
                                    "timestamp": group_date,
                                    "MildInfections": values_list[0],
                                    "Hospitalized": values_list[0],
                                    "ICU": values_list[0],
                                    "Dead": values_list[0]

                                }
                            )
                df = pd.DataFrame(rows)
                infection_rows = df.to_dict("records")
                tasks.create_multiple_infectiondata_from_dicts(infection_rows)

            tasks.create_run_simulations(
                run_id=run_id, scenario_id=scenario_id, timestamp=scenario_timestamp
            )
        return ID(id=run_id)

    def delete_simulations_run_by_id(self, run_id, scenario_id):
        tasks.delete_simulations_run_by_id(run_id)
        return {"message": f"Scenario with id: {run_id} deleted"}
