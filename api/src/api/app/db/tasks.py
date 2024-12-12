from typing import List
from uuid import uuid4
from pydantic import StrictStr

from app.db import get_session

import app.db.models as db
from app.models import *

from app.utils.constants import MovementFilter
from app.utils.defaultDict import County, age_groups

from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from sqlmodel import select


## Compartments ##
def compartment_create(compartment: Compartment) -> ID:
    # TODO Create compartment & return id
    return ID(id="")

def compartment_delete(id: StrictStr) -> None:
    # TODO check if compartment exists or is used anywhere
    # TODO delete
    return

def compartment_get_all() -> List[Compartment]:
    # TODO get & return all Compartments
    return []


## Groups ##
def group_create(group: Group) -> ID:
    group_obj = db.Group(name=group.name, description=group.description, category=group.category)
    with next(get_session()) as session:
        session.add(group_obj)
        session.commit()
        session.refresh(group_obj)
    return ID(id=group_obj.id)

def group_delete_by_id(id: StrictStr) -> None:
    query = select(db.Group).where(db.Group.id == id)
    with next(get_session()) as session:
        group: db.Group = session.exec(query).one_or_none()
        if not group:
            return Error()
            raise HTTPException(status_code=409, detail='A group with this ID does not exist')
        # TODO check if group is used anywhere and raise Exception
        # TODO delete
    return

def group_get_all() -> List[ID]:
    return [] # TODO select and return all groups

def group_get_all_categories() -> List[str]:
    return [] # TODO select and return all categories


## Intervention Templates ##
def intervention_template_create(intervention: InterventionTemplate) -> ID:
    # TODO create and return id
    return ID(id="")

def intervention_template_delete(id: StrictStr) -> None:
    # TODO check if exists or used and raise exception
    # TODO delete
    return

def intervention_template_get_all() -> List[InterventionTemplate]:
    # TODO select and return all templates
    return []


## Models ##
def model_create(model: Model) -> ID:
    # TODO create and return id
    return ID(id="")

def model_delete() -> None:
    # TODO check if exists or used and raise exception
    # TODO delete
    return

def model_get_by_id(id: StrictStr) -> Model:
    # TODO select and return model with id
    return Model()

def model_get_all():
    # TODO get all and return reduced info
    return List[ReducedInfo]


## Nodes ##
def node_create(node: Node) -> ID:
    # TODO create and return id
    return ID(id="")

def node_get_all() -> List[Node]:
    # TODO get and return all nodes
    return []

def node_delete(id: StrictStr) -> None:
    # TODO check if exists or used and raise exception
    # TODO delete
    return


## Nodelists ##
def nodelist_create(nodeList: NodeList) -> ID:
    # TODO create nodelist and return id
    return ID(id="")

def nodelist_get_by_id(id: ID) -> NodeList:
    # TODO get and return specific nodelist
    return NodeList()
def nodelist_get_all() -> List[ReducedInfo]:
    # TODO get all nodelists and return reduced infos
    return []
def nodelist_delete() -> None:
    # TODO check if exists or used and raise ex
    # TODO delete
    return


## Parameter Definitions ##
def parameter_definition_create(parameter: ParameterDefinition) -> ID:
    # TODO create definition and return id
    return ID(id="")

def parameter_definition_get_all() -> List[ParameterDefinition]:
    # TODO get and return all definitions
    return []

def parameter_definition_delete(id: StrictStr) -> None:
    # TODO check if exists or used and raise ex
    # TODO delete
    return


def create_new_group(name: str, description: str, category: str, id: str):
    data_obj = Group(name=name, description=description, category=category, id=id)
    with next(get_session()) as session:
        session.add(data_obj)
        session.commit()

def create_groups(group_maps):
    # remove key "Total" from group maps 
    del group_maps["Total"]
    category = "age"
    for group_id, group_name in group_maps.items():
        grp_idx = group_name.split("_")[1]
        des = age_groups[int(grp_idx)]
        create_new_group(group_name, des, category, group_id)

def get_all_group():
    statement = select(Group)
    with next(get_session()) as session:
        query_results: Group = session.exec(statement).all()
    if query_results:
        return query_results


def get_group_by_id(id: str):
    statement = select(Group).where(Group.id == id)
    with next(get_session()) as session:
        query_results: Group = session.exec(statement).one_or_none()
    if query_results:
        return query_results


def delete_group_by_id(id: str):
    statement = select(Group).where(Group.id == id)
    with next(get_session()) as session:
        group = session.exec(statement).one_or_none()
        if group:
            session.delete(group)
            session.commit()
            return id


# Interventions


def create_new_intervention(name: str, description: str, id: str):
    data_obj = Intervention(name=name, description=description, id=id)
    with next(get_session()) as session:
        session.add(data_obj)
        session.commit()


def get_all_interventions():
    statement = select(Intervention)
    with next(get_session()) as session:
        query_results: Intervention = session.exec(statement).all()
    if query_results:
        return query_results


def get_intervention_by_id(id: str):
    statement = select(Intervention).where(Intervention.id == id)
    with next(get_session()) as session:
        query_results: Intervention = session.exec(statement).one_or_none()
    if query_results:
        return query_results


def delete_intervention_by_id(id: str):
    statement = select(Intervention).where(Intervention.id == id)
    with next(get_session()) as session:
        results = session.exec(statement)
        intervention = results.one()
        session.delete(intervention)
        session.commit()


# ParameterDefinitions


def create_new_parameter_definition(name: str, description: str, id: str):
    data_obj = ParameterDefinition(name=name, description=description, id=id)
    with next(get_session()) as session:
        session.add(data_obj)
        session.commit()


def get_all_parameter_definitions():
    statement = select(ParameterDefinition)
    with next(get_session()) as session:
        query_results: ParameterDefinition = session.exec(statement).all()
    if query_results:
        return query_results


def get_parameter_definition_by_id(id: str):
    statement = select(ParameterDefinition).where(ParameterDefinition.id == id)
    with next(get_session()) as session:
        query_results: ParameterDefinition = session.exec(statement).one_or_none()
    if query_results:
        return query_results


def delete_parameter_definition_by_id(id: str):
    statement = select(ParameterDefinition).where(ParameterDefinition.id == id)
    with next(get_session()) as session:
        results = session.exec(statement)
        parameter_definition = results.one()
        session.delete(parameter_definition)
        session.commit()


# Nodes
def create_new_node(name: str, description: str, id: str):
    data_obj = Node(name=name, description=description, id=id)
    with next(get_session()) as session:
        session.add(data_obj)
        session.commit()

def create_nodes(node_id: str):
    node_county = County[int(node_id)]

    # get name and description of node by splitting the string
    splitted_county = node_county.split(",")
    name = splitted_county[0]
    if len(splitted_county) == 2:
        description = splitted_county[1]
    else:
        description = ""
    # add 0 to node id if the length of node id is not equal to 5
    if len(node_id) != 5:
        node_id = "0" + node_id
    data_obj = Node(name=name, description=description, id=node_id)
    with next(get_session()) as session:
        session.add(data_obj)
        session.commit()


def get_all_nodes():
    statement = select(Node)
    with next(get_session()) as session:
        query_results: Node = session.exec(statement).all()
    if query_results:
        return query_results


def _get_node_by_id(id: str):
    statement = select(Node).where(Node.id == id)
    with next(get_session()) as session:
        query_results: Node = session.exec(statement).one_or_none()
    if query_results:
        return query_results


def _delete_node_by_id(id: str):
    statement = select(Node).where(Node.id == id)
    with next(get_session()) as session:
        results = session.exec(statement)
        node = results.one()
        session.delete(node)
        session.commit()


# nodelists


def create_node_list(name: str, description: str, nodeIds: list, id: str):
    list_of_nodes = []
    for node_id in nodeIds:
        node = _get_node_by_id(node_id)
        if node:
            list_of_nodes.append(node)
        else:
            raise ValueError(f"Node with id: '{node_id}' not found!")
    data_obj = NodeList(name=name, description=description, nodes=list_of_nodes, id=id)
    with next(get_session()) as session:
        session.add(data_obj)
        session.commit()


def get_all_nodelists():
    statement = select(NodeList)
    with next(get_session()) as session:
        query_results: NodeList = session.exec(statement).all()
    if query_results:
        return query_results


def _get_nodelist_by_id(id: str):
    statement = select(NodeList).where(NodeList.id == id)
    with next(get_session()) as session:
        query_results: NodeList = session.exec(statement).one_or_none()
        if query_results:
            result = NodeListAPI(
                name=query_results.name,
                description=query_results.description,
                id=query_results.id,
                nodeIds=[[node.id for node in query_results.nodes]],
            )
            return result


def _delete_nodelist_by_id(id: str):
    statement = select(NodeList).where(NodeList.id == id)
    with next(get_session()) as session:
        results = session.exec(statement)
        nodelist = results.one()
        session.delete(nodelist)
        session.commit()


def create_new_compartment(comp):
    data_obj = comp
    with next(get_session()) as session:
        session.add(data_obj)
        session.commit()


def create_new_tag(id: str, name: str):
    data_obj = Tag(id=id, name=name)
    with next(get_session()) as session:
        session.add(data_obj)
        session.commit()


def get_tags_by_ids(ids: list):
    statement = select(Tag).where(Tag.id in ids)
    with next(get_session()) as session:
        query_results: Tag = session.exec(statement).all()
    if query_results:
        return query_results


# Models
def create_new_model(
    id: str,
    name: str,
    description: str,
    compartment: list,
    groups: list,
    parameter_definitions: list,
):
    grs = []
    prds = []
    comps = []
    # tags = []

    for comp in compartment:
        create_new_compartment(comp=comp)
        comps.append(comp)

    for group_id in groups:
        group = get_group_by_id(group_id[0])
        # check if the group id is present
        if not group:
            raise HTTPException(
                status_code=404, detail=f"Group id {group_id[0]} does not exists"
            )
        grs.append(group)

    for parameter_id in parameter_definitions:
        parameter_definition = get_parameter_definition_by_id(parameter_id[0])
        # check if the parameter id is present
        if not parameter_definition:
            raise HTTPException(
                status_code=404,
                detail=f"Group id {parameter_definition[0]} does not exists",
            )
        prds.append(parameter_definition)

    data_obj = Model(
        id=id,
        name=name,
        description=description,
        compartments=comps,
        groups=grs,
        parameter_definitions=prds,
    )
    with next(get_session()) as session:
        session.add(data_obj)
        session.commit()


def get_all_models():
    statement = select(Model)
    with next(get_session()) as session:
        query_results: Model = session.exec(statement).all()
    if query_results:
        return query_results


def _get_model_by_id(id: str):
    statement = select(Model).where(Model.id == id)
    with next(get_session()) as session:
        query_results: Model = session.exec(statement).one_or_none()

        if query_results:
            grps = []
            prds = []
            comps = []
            aggs = []

            for agg in query_results.aggregations:
                agg_id = agg.id
                aggs.append([agg_id])

            for comp in query_results.compartments:
                comp = Model_Compartment(
                    name=comp.name, description=comp.description, tags=[comp.tags]
                )
                comps.append(comp)

            for group in query_results.groups:
                grp = group.id
                grps.append([grp])

            for params in query_results.parameter_definitions:
                prd = params.id
                prds.append([prd])

            model = Model_Model(
                id=query_results.id,
                name=query_results.name,
                description=query_results.description,
                aggregations=aggs,
                compartments=comps,
                groups=grps,
                parameterDefinitions=prds,
            )
            return model
        else:
            raise HTTPException(
                status_code=404, detail=f"Model id <{id}> does not exists"
            )


def _delete_model_by_id(id: str):
    statement = select(Model).where(Model.id == id)
    with next(get_session()) as session:
        results = session.exec(statement)
        node = results.one()
        session.delete(node)
        session.commit()


# scenarios


def create_data_object(data_obj):
    with next(get_session()) as session:
        session.add(data_obj)
        session.commit()


def create_new_scenario(
    id: str,
    name: str,
    description: str,
    model_id: str,
    node_list_id: str,
    linked_interventions_ids: list,
    model_paramters: List[ParameterValue],
):
    node_list = _get_nodelist_by_id(node_list_id)

    # verify if the interventions exists and add it to list
    list_of_linked_interventions = []
    for intervention in linked_interventions_ids:
        intervention_id = intervention.id
        intervention = get_intervention_by_id(intervention_id)
        if intervention:
            list_of_linked_interventions.append(intervention)

    model_paramter_list = []
    group_list = []
    category_list = []
    for parameter in model_paramters:
        for p_group in parameter.groups:
            group = get_group_by_id(p_group.group_id)

            # verify if group_id exists or not
            if group:
                data_obj = GroupParameterValueRange(
                    id=p_group.group_id,
                    value_min_inclusiv=p_group.value_min_inclusiv,
                    value_max_exclusiv=p_group.value_max_exclusiv,
                )

                # adds group object to GroupParameterValueRange table
                create_data_object(data_obj)
                group_list.append(data_obj)
        for p_category in parameter.categories:
            category = get_group_by_id(p_category.group_id)
            if category:
                data_obj = CategoryParameterValueRange(
                    id=p_group.group_id,
                    value_min_inclusiv=p_group.value_min_inclusiv,
                    value_max_exclusiv=p_group.value_max_exclusiv,
                )

                # adds group object to CategoryParameterValueRange table
                print("+" * 100)
                print(
                    data_obj.id,
                    data_obj.value_max_exclusiv,
                    data_obj.value_min_inclusiv,
                )
                create_data_object(data_obj)
                category_list.append(data_obj)

        # check if parameter id exists or not
        parameter_obj = get_parameter_definition_by_id(parameter.parameter_id)
        if parameter_obj:
            model_parameter_obj = ParameterValue(
                id=parameter.parameter_id, groups=group_list, categories=category_list
            )
            # adds group object to ParameterValue table
            create_data_object(model_parameter_obj)
            model_paramter_list.append(model_parameter_obj)

    if node_list:
        scenario_data_obj = Scenario(
            id=id,
            name=name,
            description=description,
            model_id=model_id,
            node_list_id=node_list_id,
            linked_interventions=list_of_linked_interventions,
            parameter_values=model_paramter_list,
        )

        create_data_object(scenario_data_obj)


def get_migrations_for_node(
    scenario_id,
    run_id,
    compartments,
    node,
    start_date,
    end_date,
    groups,
):
    statement = select(Migration).where(
        Migration.scenario_id == scenario_id,
        Migration.run_id == run_id,
    )

    if node:
        statement = statement.where(
            Migration.start_node == node or Migration.end_node == node
        )
    if start_date and end_date:
        statement = statement.where(Migration.timestamp.between(start_date, end_date))
    if compartments:
        statement = statement.where(Migration.compartment_name.in_(compartments))
    if groups:
        statement = statement.where(Migration.group_id.in_(groups))

    with next(get_session()) as session:
        query_results: Migration = session.exec(statement).all()
    if query_results:
        return query_results


def get_migrations(
    scenario_id,
    run_id,
    start_node,
    end_nodes,
    start_date,
    end_date,
    compartments,
    groups,
):
    statement = select(Migration).where(
        Migration.scenario_id == scenario_id,
        Migration.run_id == run_id,
    )

    if start_node:
        statement = statement.where(Migration.start_node == start_node)
    if end_nodes:
        statement = statement.where(Migration.end_node.in_(end_nodes))
    if start_date and end_date:
        statement = statement.where(Migration.timestamp.between(start_date, end_date))
    if compartments:
        statement = statement.where(Migration.compartment_name.in_(compartments))
    if groups:
        statement = statement.where(Migration.group_id.in_(groups))

    with next(get_session()) as session:
        query_results: Migration = session.exec(statement).all()
    if query_results:
        return query_results


def get_all_movements_for_cell(
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
):
    statement = select(Movements).where(
        Movements.scenario_id == scenario_id,
        Movements.run_id == run_id,
    )
    if start_date and end_date:
        statement = statement.where(Movements.timestamp.between(start_date, end_date))
    if compartments:
        statement = statement.where(Movements.compartment_name.in_(compartments))
    if groups:
        statement = statement.where(Movements.group_id.in_(groups))
    if cells:
        if movement_filter == MovementFilter.START:
            statement = statement.where(Movements.start_cell.in_(cells))
        elif movement_filter == MovementFilter.END:
            statement = statement.where(Movements.end_cell.in_(cells))
        elif movement_filter == MovementFilter.START_AND_END:
            statement = statement.where(
                Movements.start_cell.in_(cells) and Movements.end_cell.in_(cells)
            )
        else:
            statement = statement.where(
                Movements.start_cell.in_(cells) or Movements.end_cell.in_(cells)
            )
    if travel_mode:
        statement = statement.where(Movements.travel_mode.in_(travel_mode))
    if activity:
        statement = statement.where(Movements.activity.in_(activity))
    if min_travel_time and max_travel_time:
        statement = statement.where(
            Movements.timestamp.between(min_travel_time, max_travel_time)
        )

    with next(get_session()) as session:
        query_results: Movements = session.exec(statement).all()
    if query_results:
        return query_results


def get_all_scenarios():
    statement = select(Scenario)
    with next(get_session()) as session:
        query_results: Scenario = session.exec(statement).all()
    if query_results:
        return query_results


def get_scenario_obj(id: str):
    statement = select(Scenario).where(Scenario.id == id)
    with next(get_session()) as session:
        query_results: Scenario = session.exec(statement).one()
    if query_results:
        return query_results


def get_scenario_by_id(id: str):
    statement = select(Scenario).where(Scenario.id == id)
    with next(get_session()) as session:
        query_results: Scenario = session.exec(statement).one_or_none()

        try:
            if query_results:
                groups = []
                categories = []
                parameter_values = []
                linked_interventions = []
                run_id_list = []

                run_simulations = query_results.runsimulations
                for run_simulation in run_simulations:
                    run_id_list.append(
                        ScenarioRunsRunIdListInner(
                            run_id=run_simulation.run_id,
                            timestamp=run_simulation.timestamp,
                        )
                    )
                for parameter_value in query_results.parameter_values:
                    for group in parameter_value.groups:
                        grp = ModelParamaterValueRange(
                            groupId=group.id,
                            valueMinInclusiv=group.value_min_inclusiv,
                            valueMaxExclusiv=group.value_max_exclusiv,
                        )
                        groups.append(grp)

                    for category in parameter_value.categories:
                        cat = ModelParamaterValueRange(
                            groupId=category.id,
                            valueMinInclusiv=category.value_min_inclusiv,
                            valueMaxExclusiv=category.value_max_exclusiv,
                        )
                        categories.append(cat)

                    par_val = ModelParameterValue(
                        parameterId=parameter_value.id,
                        groups=groups,
                        categories=categories,
                    )
                    parameter_values.append(par_val)

                for intervention in query_results.linked_interventions:
                    intervention_id = intervention.id
                    intervention_dict = {"id": intervention_id}
                    linked_interventions.append(intervention_dict)

                scenario = ModelScenario(
                    id=query_results.id,
                    name=query_results.name,
                    description=query_results.description,
                    modelId=query_results.model_id,
                    modelParameters=parameter_values,
                    nodeListId=query_results.node_list_id,
                    linkedInterventions=linked_interventions,
                    run_id_list=run_id_list,
                )

                return scenario
        except:  # noqa: E722 TODO: resolve bare except
            raise HTTPException(
                status_code=404, detail=f"Scenario id <{id}> does not exists"
            )


def delete_scenario_by_id(id: str):
    statement = select(Scenario).where(Scenario.id == id)
    with next(get_session()) as session:
        results = session.exec(statement)
        scenario = results.one()
        session.delete(scenario)
        session.commit()


def check_scenario(scenario_id: str, run_id: str):
    scenario = get_scenario_by_id(scenario_id)
    statement = select(RunSimulations).where(RunSimulations.run_id == run_id)
    with next(get_session()) as session:
        query_results: RunSimulations = session.exec(statement).one_or_none()
    if query_results and scenario:
        return True
    else:
        return False


def create_run_simulations(run_id: str, scenario_id: str, timestamp: str):
    scenario = get_scenario_obj(scenario_id)
    data_obj = RunSimulations(
        run_id=run_id, scenario_id=scenario_id, timestamp=timestamp, scenario=scenario
    )
    try:
        with next(get_session()) as session:
            session.add(data_obj)
            session.commit()
    except IntegrityError:
        raise HTTPException(
            status_code=404,
            detail=f"Key (scenario_id)=({scenario_id}) is not present in table <scenario>",
        )


def delete_simulations_run_by_id(id: str):
    statement = select(RunSimulations).where(RunSimulations.run_id == id)
    with next(get_session()) as session:
        results = session.exec(statement)
        simulations_run = results.one()
        session.delete(simulations_run)
        session.commit()


def create_new_infectiondata(timestamp: str, node: str, value: str):
    data_obj = InfectionData(timestamp=timestamp, node=node, value=value)
    with next(get_session()) as session:
        session.add(data_obj)
        session.commit()

def get_infection_data(timestamp: str, node: str, group: str):
    statement = select(InfectionData).where(InfectionData.timestamp==timestamp, InfectionData.node==node, InfectionData.group==group)
    with next(get_session()) as session:
        query_results: InfectionData = session.exec(statement).all()
        if query_results:
            return query_results

def create_multiple_infectiondata_from_dicts(infection_rows: List[dict]):
    data_objs = []
    for infection_row in infection_rows:
        data_objs.append(InfectionData(id=str(uuid4()), **infection_row))
    with next(get_session()) as session:
        for data_obj in data_objs:
            session.add(data_obj)
        session.commit()


def get_compartments_from_aggregation(compaggr_name):
    statement = select(CompartmentAggregation).where(
        CompartmentAggregation.name == compaggr_name
    )
    with next(get_session()) as session:
        query_results: CompartmentAggregation = session.exec(statement).one()
        if query_results:
            return query_results.compartments
