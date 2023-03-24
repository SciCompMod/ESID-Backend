from app.db import get_session
from app.db.models import (Group, CompartmentAggregation, Compartment, Intervention, ParameterDefinition, Node, NodeList, Model, Aggregation, Tag, RunSimulations,
                           ParameterValue, GroupParameterValueRange, CategoryParameterValueRange, Scenario, InfectionData)
from app.models.model import Model as Model_Model
from app.models.compartment import Compartment as Model_Compartment
from app.models.aggregation import Aggregation as Model_Aggregation
from app.models.tag import Tag as Model_Tag
from app.models.group import Group as Model_Group
from app.models.node_list import NodeList as NodeListAPI
from app.models.scenario import Scenario as ModelScenario
from app.models.parameter_value import ParameterValue as ModelParameterValue
from app.models.parameter_value_range import ParameterValueRange as ModelParamaterValueRange

from sqlmodel import select
from typing import List
from fastapi import HTTPException
from uuid import uuid4
from sqlalchemy.exc import IntegrityError
# Groups


def create_new_group(name: str, description: str, category: str, id: str):
    data_obj = Group(name=name, description=description,
                     category=category, id=id)
    with next(get_session()) as session:
        session.add(data_obj)
        session.commit()


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
        query_results: ParameterDefinition = session.exec(
            statement).one_or_none()
    if query_results:
        return query_results


def delete_parameter_definition_by_id(id: str):
    statement = select(ParameterDefinition).where(ParameterDefinition.id == id)
    with next(get_session()) as session:
        results = session.exec(statement)
        parameter_definition = results.one()
        session.delete(parameter_definition)
        session.commit()


def create_new_aggregation(id: str, name: str, description: str, tags:List):
    all_tags = []
    for tag in tags:
        tag_id= str(uuid4())
        # create_new_tag(tag_id, tag.name)
        all_tags.append(Tag(id=tag_id, name=tag.name))
    data_obj = Aggregation(name=name, description=description, id=id, tags=all_tags)
    with next(get_session()) as session:
        session.add(data_obj)
        session.commit()


def get_all_aggregations():
    statement = select(Aggregation)
    with next(get_session()) as session:
        query_results: Aggregation = session.exec(statement).all()
    if query_results:
        return query_results


def get_aggregation_by_id(id: str):
    statement = select(Aggregation).where(Aggregation.id == id)
    with next(get_session()) as session:
        query_results: Aggregation = session.exec(
            statement).one_or_none()
        if query_results:
            tags = []
            for tag in query_results.tags:
                tags.append(Model_Tag(name=tag.name))
            return Model_Aggregation(id=query_results.id,
                                    name=query_results.name,
                                    description=query_results.description,
                                    tags=query_results.tags
                                    )
        else:
            raise HTTPException(
                status_code=404, detail=f"Aggregation id <{id}> does not exists")


def delete_aggregation_by_id(id: str):
    statement = select(Aggregation).where(Aggregation.id == id)
    with next(get_session()) as session:
        results = session.exec(statement)
        aggregation = results.one()
        session.delete(aggregation)
        session.commit()


# Nodes
def create_new_node(name: str, description: str, id: str):
    data_obj = Node(name=name, description=description, id=id)
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
    data_obj = NodeList(name=name, description=description,
                        nodes=list_of_nodes, id=id)
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
            result = NodeListAPI(name=query_results.name,
                                 description=query_results.description,
                                 id=query_results.id,
                                 nodeIds=[
                                     [node.id for node in query_results.nodes]]
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
    data_obj = Tag(id=id,name=name)
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
def create_new_model(id: str, name: str, description: str, compartment: list, groups: list, aggregation_ids: list, parameter_definitions: list):
    grs = []
    prds = []
    comps = []
    # tags = []
    list_of_aggregations = []
    for agg_id in aggregation_ids:
        agg = get_aggregation_by_id(agg_id[0])
        if agg:
            list_of_aggregations.append(agg)
        else:
            raise ValueError(f"Aggregation with id: '{agg_id}' not found!")

    for comp in compartment:
        create_new_compartment(comp=comp)
        comps.append(comp)

    for group_id in groups:
        group = get_group_by_id(group_id[0])
        # check if the group id is present
        if not group:
            raise HTTPException(
                status_code=404, detail=f"Group id {group_id[0]} does not exists")
        grs.append(group)

    for parameter_id in parameter_definitions:
        parameter_definition = get_parameter_definition_by_id(parameter_id[0])
        # check if the parameter id is present
        if not parameter_definition:
            raise HTTPException(
                status_code=404, detail=f"Group id {parameter_definition[0]} does not exists")
        prds.append(parameter_definition)

    data_obj = Model(id=id, name=name, description=description, compartments=comps,
                     groups=grs, aggregations=list_of_aggregations, parameter_definitions=prds)
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
            aggs=[]

            for agg in query_results.aggregations:
                agg_id = agg.id
                aggs.append([agg_id])

            for comp in query_results.compartments:
                comp = Model_Compartment(
                    name=comp.name, description=comp.description, tags=[comp.tags])
                comps.append(comp)

            for group in query_results.groups:
                grp = group.id
                grps.append([grp])

            for params in query_results.parameter_definitions:
                prd = params.id
                prds.append([prd])

            model = Model_Model(id=query_results.id,
                                name=query_results.name, description=query_results.description, aggregations=aggs,
                                compartments=comps, groups=grps, parameterDefinitions=prds)
            return model
        else:
            raise HTTPException(
                status_code=404, detail=f"Model id <{id}> does not exists")


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


def create_new_scenario(id: str, name: str, description: str, model_id: str, node_list_id: str, linked_interventions_ids: list, model_paramters: List[ParameterValue]):
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
                    id=p_group.group_id, value_min_inclusiv=p_group.value_min_inclusiv, value_max_exclusiv=p_group.value_max_exclusiv)

                # adds group object to GroupParameterValueRange table
                create_data_object(data_obj)
                group_list.append(data_obj)
        for p_category in parameter.categories:
            category = get_group_by_id(p_category.group_id)
            if category:
                data_obj = CategoryParameterValueRange(
                    id=p_group.group_id, value_min_inclusiv=p_group.value_min_inclusiv, value_max_exclusiv=p_group.value_max_exclusiv)

                # adds group object to CategoryParameterValueRange table
                create_data_object(data_obj)
                category_list.append(data_obj)

        # check if parameter id exists or not
        parameter_obj = get_parameter_definition_by_id(parameter.parameter_id)
        if parameter_obj:
            model_parameter_obj = ParameterValue(
                id=parameter.parameter_id, groups=group_list, categories=category_list)
            # adds group object to ParameterValue table
            create_data_object(model_parameter_obj)
            model_paramter_list.append(model_parameter_obj)

    if node_list:
        scenario_data_obj = Scenario(id=id,
                                     name=name,
                                     description=description,
                                     model_id=model_id,
                                     node_list_id=node_list_id,
                                     linked_interventions=list_of_linked_interventions,
                                     parameter_values=model_paramter_list)

        create_data_object(scenario_data_obj)


def get_all_scenarios():
    statement = select(Scenario)
    with next(get_session()) as session:
        query_results: Scenario = session.exec(statement).all()
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

                for parameter_value in query_results.parameter_values:
                    for group in parameter_value.groups:
                        grp = ModelParamaterValueRange(
                            groupId=group.id, valueMinInclusiv=group.value_min_inclusiv, valueMaxExclusiv=group.value_max_exclusiv)
                        groups.append(grp)

                    for category in parameter_value.categories:
                        cat = ModelParamaterValueRange(
                            groupId=category.id, valueMinInclusiv=category.value_min_inclusiv, valueMaxExclusiv=category.value_max_exclusiv)
                        categories.append(cat)

                    par_val = ModelParameterValue(
                        parameterId=parameter_value.id, groups=groups, categories=categories)
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
                    linkedInterventions=linked_interventions
                )

                return scenario
        except:
            raise HTTPException(
                status_code=404, detail=f"Scenario id <{id}> does not exists")


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


def create_run_simulations(run_id: str, scenario_id: str):
    data_obj = RunSimulations(run_id=run_id, scenario_id=scenario_id)
    try:
        with next(get_session()) as session:
            session.add(data_obj)
            session.commit()
    except IntegrityError:
        raise HTTPException(
            status_code=404, detail=f"Key (scenario_id)=({scenario_id}) is not present in table <scenario>")


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


def create_multiple_infectiondata_from_dicts(infection_rows: List[dict]):
    data_objs = []
    for infection_row in infection_rows:
        data_objs.append(InfectionData(id= str(uuid4()),**infection_row))
    with next(get_session()) as session:
        for data_obj in data_objs:
            session.add(data_obj)
        session.commit()
