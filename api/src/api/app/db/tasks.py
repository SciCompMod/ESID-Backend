from collections import defaultdict
import json
from typing import List, Optional, Union
from uuid import uuid4
from pydantic import StrictInt, StrictStr
from datetime import date, datetime, time

from app.db import get_session

import app.db.models as db
from app.models import *

from app.utils.constants import MovementFilter
from app.utils.defaultDict import County, age_groups

from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import selectinload
from sqlmodel import select


## Compartments ##
def compartment_create(compartment: Compartment) -> ID:
    compartment_obj = db.Compartment(
        name=compartment.name,
        description=compartment.description,
        tags=','.join(compartment.tags) if compartment.tags else None,
        )
    with next(get_session()) as session:
        session.add(compartment_obj)
        session.commit()
        session.refresh(compartment_obj)
    return ID(id=str(compartment_obj.id))

def compartment_delete(id: StrictStr) -> None:
    query = select(db.Compartment).where(db.Compartment.id == id).options(selectinload(db.Compartment.modelLinks))
    with next(get_session()) as session:
        compartment: db.Compartment = session.exec(query).one_or_none()
        if not compartment:
            raise HTTPException(status_code=404, detail='A compartment with this ID does not exist')
        if len(compartment.modelLinks) > 0:
            raise HTTPException(status_code=409, detail='Compartment is still linked to models: {}'.format( ', '.join([str(link.modelId) for link in compartment.modelLinks])))
        session.delete(compartment)
        session.commit()
    return

def compartment_get_all() -> List[Compartment]:
    query = select(db.Compartment)
    with next(get_session()) as session:
        compartments: List[db.Compartment] = session.exec(query).all()
    return [Compartment(
        id=str(compartment.id),
        name=compartment.name,
        description=compartment.description,
        tags=compartment.tags.split(',') if compartment.tags else None
    ) for compartment in compartments]


## Groups ##
def group_create(group: Group) -> ID:
    group_obj = db.Group(
        name=group.name,
        description=group.description,
        category=group.category
    )
    with next(get_session()) as session:
        session.add(group_obj)
        session.commit()
        session.refresh(group_obj)
    return ID(id=str(group_obj.id))

def group_delete_by_id(id: StrictStr) -> None:
    query = select(db.Group).where(db.Group.id == id).options(selectinload(db.Group.parameterValueEntries)).options(selectinload(db.Group.modelLinks))
    with next(get_session()) as session:
        group: db.Group = session.exec(query).one_or_none()
        if not group:
            raise HTTPException(status_code=404, detail='A group with this ID does not exist')
        message = {}
        if len(group.parameterValueEntries) > 0:
            message['parameterValues'] = 'Group is still linked to parameter values: {}'.format(', '.join([str(entry.id) for entry in group.parameterValueEntries]))
        if len(group.modelLinks) > 0:
            message['models'] = 'Group is still linked to models: {}'.format(', '.join([str(link.modelId) for link in group.modelLinks]))
        if message:
            raise HTTPException(status_code=409, detail=message)
        session.delete(group)
        session.commit()
    return

def group_get_all() -> List[ID]:
    query = select(db.Group)
    with next(get_session()) as session:
        groups: List[db.Group] = session.exec(query).all()
    return [Group(
        id=str(group.id),
        name=group.name,
        description=group.description,
        category=group.category
    ) for group in groups]

def group_get_all_categories() -> List[str]:
    query = select(db.Group.category).distinct()
    with next(get_session()) as session:
        categories: List[str] = session.exec(query).all()
    return categories


## Intervention Templates ##
def intervention_template_create(intervention: InterventionTemplate) -> ID:
    template_obj = db.InterventionTemplate(
        name=intervention.name,
        description=intervention.description,
        tags=','.join(intervention.tags) if intervention.tags else None,
    )
    with next(get_session()) as session:
        session.add(template_obj)
        session.commit()
        session.refresh(template_obj)
    return ID(id=str(template_obj.id))

def intervention_template_delete(id: StrictStr) -> None:
    query = select(db.InterventionTemplate).where(db.InterventionTemplate.id == id).options(selectinload(db.InterventionTemplate.implementations))
    with next(get_session()) as session:
        template: db.InterventionTemplate = session.exec(query).one_or_none()
        if not template:
            raise HTTPException(status_code=404, detail="An intervention template with this ID does not exist")
        if len(template.implementations) > 0:
            raise HTTPException(status_code=409, detail='Intervention template is still used in scenario: {}'.format( ', '.join([str(link.scenarioId) for link in template.implementations])))
        session.delete(template)
        session.commit()
    return

def intervention_template_get_all() -> List[InterventionTemplate]:
    query = select(db.InterventionTemplate)
    with next(get_session()) as session:
        templates: List[db.InterventionTemplate] = session.exec(query).all()
    return [InterventionTemplate(
        id=str(entry.id),
        name=entry.name,
        description=entry.description,
        tags=entry.tags.split(',') if entry.tags else None
    ) for entry in templates]


## Models ##
def model_create(model: Model) -> ID:
    model_obj = db.Model(
        name=model.name,
        description=model.description,
        # compartments=model.compartments                   Links for compartments
        # groups=model.groups                               Links for groups
        # parameterDefinitions=model.parameter_definitions  Links for parameter definitions
    )
    with next(get_session()) as session:
        message = {}
        # Check compartments are valid
        foundCompartments: List[db.Compartment] = session.exec(
            select(db.Compartment).where(db.Compartment.id.in_(model.compartments))
        ).all()
        if not len(foundCompartments) == len(model.compartments):
            wrongCompartments = list(set(model.compartments).difference([str(compartment.id) for compartment in foundCompartments]))
            message['compartments'] = 'One or more Compartment IDs do not exist in compartment table. Unknown compartments: {}'.format( ', '.join(wrongCompartments))
        # Check groups are valid
        foundGroups: List[db.Group] = session.exec(
            select(db.Group).where(db.Group.id.in_(model.groups))
        ).all()
        if not len(foundGroups) == len(model.groups):
            wrongGroups = list(set(model.groups).difference([str(group.id) for group in foundGroups]))
            message['groups'] = 'One or more Group IDs do not exist in group table. Unknown groups: {}'.format( ', '.join(wrongGroups))
        # Check parameter definitions are valid
        foundParameters: List[db.ParameterDefinition] = session.exec(
            select(db.ParameterDefinition).where(db.ParameterDefinition.id.in_(model.parameter_definitions))
        ).all()
        if not len(foundParameters) == len(model.parameter_definitions):
            wrongParameters = list(set(model.parameter_definitions).difference([str(param.id) for param in foundParameters]))
            message['parameter_definitions'] = 'One or more Parameter Definition IDs do not exist in parameter definition table. Unknown parameter definitions: {}'.format( ', '.join(wrongParameters))
        # Raise Exception if any validation issues found
        if message:
            raise HTTPException(status_code=422, detail=message)

        # Otherwise create object & Link Table entries TODO parallelize write ops like these?
        session.add(model_obj)
        # Compartment Links
        session.add_all([db.ModelCompartmentLink(
            modelId=model_obj.id,
            compartmentId=compartmentId
        ) for compartmentId in model.compartments])
        # Group Links
        session.add_all([db.ModelGroupLink(
            modelId=model_obj.id,
            groupId=groupId
        ) for groupId in model.groups])
        # Parameter Definition Links
        session.add_all([db.ModelParameterDefinitionLink(
            modelId=model_obj.id,
            parameterId=defininitionId
        ) for defininitionId in model.parameter_definitions])
        # Commit & refresh to get final object
        session.commit()
        session.refresh(model_obj)
    return ID(id=str(model_obj.id))

def model_delete(id: StrictStr) -> None:
    query = (
        select(db.Model).where(db.Model.id == id)
        .options(selectinload(db.Model.scenarios))
        )
    with next(get_session()) as session:
        model: db.Model = session.exec(query).one_or_none()
        if not model:
            raise HTTPException(status_code=404, detail='A model with this ID does not exist')
        if len(model.scenarios) > 0:
            raise HTTPException(status_code=404, detail='Model is still linked to scenarios: {}'.format(', '.join([str(link.id) for link in model.scenarios])))
        session.delete(model)
        session.commit()
    return

def model_get_by_id(id: StrictStr) -> Model:
    query = select(db.Model).where(db.Model.id == id)
    with next(get_session()) as session:
        model: db.Model = session.exec(query).one_or_none()
        if not model:
            raise HTTPException(status_code=404, detail='A model with this ID does not exist')
        compartmentIDs: List[StrictStr] = [str(compartment.compartmentId) for compartment in model.compartments]
        groupIDs: List[StrictStr] = [str(group.groupId) for group in model.groups]
        definitionIDs: List[StrictStr] = [str(definition.parameterId) for definition in model.parameterDefinitions]
    return Model(
        id=str(model.id),
        name=model.name,
        description=model.description,
        compartments=compartmentIDs,
        groups=groupIDs,
        parameterDefinitions=definitionIDs
    )

def model_get_all():
    query = select(db.Model)
    with next(get_session()) as session:
        models: List[db.Model] = session.exec(query).all()
    return [ReducedInfo(
        id=str(model.id),
        name=model.name,
        description=model.description
    ) for model in models]


## Nodes ##
def node_create(node: Node) -> ID:
    node_obj = db.Node(
        nuts=node.nuts,
        name=node.name
        )
    with next(get_session()) as session:
        session.add(node_obj)
        session.commit()
        session.refresh(node_obj)
    return ID(id=str(node_obj.id))

def node_get_all() -> List[Node]:
    query = select(db.Node)
    with next(get_session()) as session:
        nodes: List[db.Node] = session.exec(query).all()
    return [Node(
        id=str(node.id),
        nuts=node.nuts,
        name=node.name,
    ) for node in nodes]

def node_delete(id: StrictStr) -> None:
    query = select(db.Node).where(db.Node.id == id).options(selectinload(db.Node.nodelistLinks))
    with next(get_session()) as session:
        node: db.Node = session.exec(query).one_or_none()
        if not node:
            raise HTTPException(status_code=404, detail='A node with this ID does not exist')
        if len(node.nodelistLinks) > 0:
            raise HTTPException(status_code=409, detail='Node is still linked in node lists: {}'.format( ', '.join([str(link.listId) for link in node.nodelistLinks])))
        session.delete(node)
        session.commit()
    return


## Nodelists ##
def nodelist_create(nodeList: NodeList) -> ID:
    list_obj = db.NodeList(
        name=nodeList.name,
        description=nodeList.description,
        )
    query = select(db.Node).where(db.Node.id.in_(nodeList.node_ids))
    with next(get_session()) as session:
        # Check Nodes are valid
        foundNodes: List[db.Node] = session.exec(query).all()
        if not len(foundNodes) == len(nodeList.node_ids):
            wrongNodes = list(set(nodeList.node_ids).difference([str(node.id) for node in foundNodes]))
            raise HTTPException(status_code=422, detail='One or more Node IDs do not exist in nodes table. Unknown nodes: {}'.format( ', '.join(wrongNodes)))
        # Create Nodelist Object
        session.add(list_obj)
        # Add Node Link Table Entries (Relations)
        session.add_all([db.NodeListNodeLink(
                nodeId=nodeId,
                listId=list_obj.id
            ) for nodeId in nodeList.node_ids])
        # Commit & refresh to get final object
        session.commit()
        session.refresh(list_obj)
    return ID(id=str(list_obj.id))

def nodelist_get_by_id(id: StrictStr) -> NodeList:
    query = select(db.NodeList).where(db.NodeList.id == id)
    with next(get_session()) as session:
        nodelist: db.NodeList = session.exec(query).one_or_none()
        if not nodelist:
            raise HTTPException(status_code=404, detail='A nodelist with this ID does not exist')
        nodeIDs: List[StrictStr] = [str(link.nodeId) for link in nodelist.nodeLinks]
    return NodeList(
        id=str(nodelist.id),
        name=nodelist.name,
        description=nodelist.description,
        nodeIds=nodeIDs
    )

def nodelist_get_all() -> List[ReducedInfo]:
    query = select(db.NodeList)
    with next(get_session()) as session:
        nodelists: List[db.NodeList] = session.exec(query).all()
    return [ReducedInfo(
        id=str(list.id),
        name=list.name,
        description=list.description
    ) for list in nodelists]

def nodelist_delete(id: StrictStr) -> None:
    query = select(db.NodeList).where(db.NodeList.id == id).options(selectinload(db.NodeList.scenarios))
    with next(get_session()) as session:
        nodelist: db.NodeList = session.exec(query).one_or_none()
        if not nodelist:
            raise HTTPException(status_code=404, detail='A nodelist with this ID does not exist')
        if len(nodelist.scenarios) > 0:
            raise HTTPException(status_code=409, detail='Nodelist is still linked to scenarios: {}'.format(', '.join([str(link.id) for link in nodelist.scenarios])))
        session.delete(nodelist)
        session.commit()
    return


## Parameter Definitions ##
def parameter_definition_create(parameter: ParameterDefinition) -> ID:
    definition_obj = db.ParameterDefinition(
        name=parameter.name,
        description=parameter.description
    )
    with next(get_session()) as sesssion:
        sesssion.add(definition_obj)
        sesssion.commit()
        sesssion.refresh(definition_obj)
    return ID(id=str(definition_obj.id))

def parameter_definition_get_all() -> List[ParameterDefinition]:
    query = select(db.ParameterDefinition)
    with next(get_session()) as session:
        definitions: List[db.ParameterDefinition] = session.exec(query).all()
    return [ParameterDefinition(
        id=str(definition.id),
        name=definition.name,
        description=definition.description
    ) for definition in definitions]

def parameter_definition_get_by_id(id: StrictStr) -> ParameterDefinition:
    query = select(db.ParameterDefinition).where(db.ParameterDefinition.id == id)
    with next(get_session()) as session:
        parameter: db.ParameterDefinition = session.exec(query).one_or_none()
        if not parameter:
            raise HTTPException(status_code=404, detail='A parameter definition with this ID does not exist')
    return ParameterDefinition(
        id=str(parameter.id),
        name=parameter.name,
        description=parameter.description
    )

def parameter_definition_delete(id: StrictStr) -> None:
    query = (
        select(db.ParameterDefinition).where(db.ParameterDefinition.id == id)
        .options(selectinload(db.ParameterDefinition.scenarioLinks))
        .options(selectinload(db.ParameterDefinition.modelLinks))
        )
    with next(get_session()) as session:
        definition: db.ParameterDefinition = session.exec(query).one_or_none()
        if not definition:
            raise HTTPException(status_code=404, detail='A parameter definition with this ID does not exist')
        message = {}
        if len(definition.scenarioLinks) > 0:
            message['scenarios'] = 'Parameter Definition is still used in scenarios: {}'.format(', '.join([str(link.scenarioId) for link in definition.scenarioLinks]))
        if len(definition.modelLinks) > 0:
            message['models'] = 'Parameter Definition is still used in models: {}'.format(', '.join([str(link.modelId) for link in definition.modelLinks]))
        if message:
            raise HTTPException(status_code=409, detail=message)
        session.delete(definition)
        session.commit()
    return


## Scenarios ##
def scenario_create(scenario: Scenario) -> ID:
    scenario_obj = db.Scenario(
        name=scenario.name,
        description=scenario.description,
        startDate=scenario.start_date,
        endDate=scenario.end_date,
        modelId=scenario.model_id,
        nodeListId=scenario.node_list_id,
        # modelParameters=scenario.model_parameters          Links for ParameterValue
        # linkedInterventions=scenario.linked_interventions  Links for InterventionImplementations
        percentiles=','.join(scenario.percentiles) if scenario.percentiles else '50',
        timestampSubmitted=datetime.now(),
        timestampSimulated=None,
    )
    with next(get_session()) as session:
        nested_dict = lambda: defaultdict(nested_dict)
        message = nested_dict()
        # validate model
        model: db.Model = session.exec(
            select(db.Model).where(db.Model.id == scenario.model_id)
            .options(selectinload(db.Model.parameterDefinitions))
            .options(selectinload(db.Model.groups))
        ).one_or_none()
        if not model:
            message['modelId'] = 'A model with this ID does not exist'
        # validate node list
        nodelist: db.NodeList = session.exec(
            select(db.NodeList).where(db.NodeList.id == scenario.node_list_id)
        ).one_or_none()
        if not nodelist:
            message['nodeListID'] = 'A nodelist with this ID does not exist'
        # validate interventions
        foundInterventions: List[db.InterventionTemplate] = session.exec(
            select(db.InterventionTemplate).where(db.InterventionTemplate.id.in_([intervention.intervention_id for intervention in scenario.linked_interventions]))
        ).all()
        if not len(foundInterventions) == len(scenario.linked_interventions):
            wrongInterventions = list(set([intervention.intervention_id for intervention in scenario.linked_interventions]).difference([str(intervention.id) for intervention in foundInterventions]))
            message['linkedInterventions'] = 'One or more linked interventions do not exist in intervention template table. Unknown interventions: {}'.format(', '.join(wrongInterventions))
        # validate parameters
        if model:
            # check each parameter matches model parameters
            params_onModel = set([str(definition.parameterId) for definition in model.parameterDefinitions])
            params_onScenario = set([impl.parameter_id for impl in scenario.model_parameters])
            if params_onModel.difference(params_onScenario):
                message['modelParameters']['missing'] = 'One or parameters of model {modelID} are not defined. Missing parameters: {params}'.format(modelID=str(model.id), params=', '.join(params_onModel.difference(params_onScenario)))
            if params_onScenario.difference(params_onModel):
                message['modelParameters']['unknown'] = 'One or more parameters do not exist in model {modelID}. Unknown parameters: {params}'.format(modelID=str(model.id), params=', '.join(params_onScenario.difference(params_onModel)))
            # check each parameter group matches model groups
            groups_onModel = set([str(group.groupId) for group in model.groups])
            for parameter in scenario.model_parameters:
                groups_onParameter = set([group.group_id for group in parameter.values])
                if groups_onModel.difference(groups_onParameter):
                    message['modelParameters'][parameter.parameter_id]['missing'] = 'One or more groups of model {modelID} are not defined. Missing groups: {groups}'.format(modelID=str(model.id), groups=', '.join(groups_onModel.difference(groups_onParameter)))
                if groups_onParameter.difference(groups_onModel):
                    message['modelParameters'][parameter.parameter_id]['unknown'] = 'One or more groups do not exist in model {modelID}. Unknown groups: {groups}'.format(modelID=str(model.id), groups=', '.join(groups_onParameter.difference(groups_onModel)))
        # Raise exception if anyvalidation issues found
        if message:
            raise HTTPException(status_code=422, detail=json.loads(json.dumps(message)))
        
        # Otherwise create Scenario & Link Table entries
        session.add(scenario_obj)
        # Intervention Implementation Links
        session.add_all([db.InterventionImplementation(
                scenarioId=scenario_obj.id,
                interventionId=intervention.intervention_id,
                startDate=intervention.start_date,
                endDate=intervention.end_date,
                coefficient=intervention.coefficient,
            ) for intervention in scenario.linked_interventions])
        # Parameter Value Links
        for parameter in scenario.model_parameters:
            session.add(db.ParameterValue(
            scenarioId=scenario_obj.id,
            definitionId=parameter.parameter_id,
            ))
            # Parameter Value Entry Links
            session.add_all([db.ParameterValueEntry(
                parameterValueIdScenario=scenario_obj.id,
                parameterValueIdDefinition=parameter.parameter_id,
                groupId=group.group_id,
                valueMin=group.value_min,
                valueMax=group.value_max,
            ) for group in parameter.values])
        session.commit()
        session.refresh(scenario_obj)
    return ID(id=str(scenario_obj.id))

def scenario_get_by_id(id: StrictStr) -> Scenario:
    query = (
        select(db.Scenario).where(db.Scenario.id == id)
        .options(selectinload(db.Scenario.modelParameters).selectinload(db.ParameterValue.values))
        .options(selectinload(db.Scenario.linkedInterventions))
        )
    with next(get_session()) as session:
        scenario: db.Scenario = session.exec(query).one_or_none()
        if not scenario:
            raise HTTPException(status_code=404, detail='a scenario with this ID does not exist')
        modelParams: List[ParameterValue] = [ParameterValue(
            parameterId=str(value.definitionId),
            values=[ParameterValueEntry(
                groupId=str(entry.groupId),
                valueMin=entry.valueMin,
                valueMax=entry.valueMax,
            ) for entry in value.values]
        ) for value in scenario.modelParameters]
        linkedInterventions=[InterventionImplementation(
            interventionId=str(intervention.interventionId),
            startDate=intervention.startDate,
            endDate=intervention.endDate,
            coefficient=intervention.coefficient,
        ) for intervention in scenario.linkedInterventions]
    return Scenario(
        id=str(scenario.id),
        name=scenario.name,
        description=scenario.description,
        startDate=scenario.startDate,
        endDate=scenario.endDate,
        modelId=str(scenario.modelId),
        modelParameters=modelParams,
        nodeListId=str(scenario.nodeListId),
        linkedInterventions=linkedInterventions,
        percentiles=[int(perc) for perc in scenario.percentiles.split(',')] if scenario.percentiles else [50],
        timestampSubmitted=scenario.timestampSubmitted,
        timestampSimulated=scenario.timestampSimulated,
    )

def scenario_get_all() -> List[ReducedScenario]:
    query = select(db.Scenario)
    with next(get_session()) as session:
        scenarios: List[db.Scenario] = session.exec(query).all()
    return [ReducedScenario(
        id=str(sc.id),
        name=sc.name,
        description=sc.description,
        startDate=sc.startDate,
        endDate=sc.endDate,
        timestampSubmitted=sc.timestampSubmitted,
        timestampSimulated=sc.timestampSimulated,
    ) for sc in scenarios]

def scenario_delete(id: StrictStr) -> None:
    query = (
        select(db.Scenario).where(db.Scenario.id == id)
    )
    with next(get_session()) as session:
        scenario: db.Scenario = session.exec(query).one_or_none()
        if not scenario:
            raise HTTPException(status_code=404, detail='A scenario with this ID does not exist')
        session.delete(scenario)
        session.commit()
    return

def scenario_get_data_by_filter(
    scenarioId: StrictStr,
    nodes: Optional[List[StrictStr]],
    start_date: Optional[date],
    end_date: Optional[date],
    compartments: Optional[List[StrictStr]],
    # aggregations: Optional[Dict[str, Dict[str, List[StrictStr]]]],
    groups: Optional[List[StrictStr]],
    percentiles: Optional[List[StrictInt]],
) -> List[Infectiondata]:
    # validate scenario ID?
    query = select(db.ScenarioDatapoint).where(db.ScenarioDatapoint.scenarioId == scenarioId)
    # if nodes supplied select only those node else return all
    if nodes:
        query = query.where(db.ScenarioDatapoint.nodeId.in_(nodes))
    if start_date:
        query = query.where(db.ScenarioDatapoint.timestamp >= datetime.combine(start_date, time.min))
    if end_date:
        query = query.where(db.ScenarioDatapoint.timestamp <= datetime.combine(end_date, time.min))
    if compartments:
        query = query.where(db.ScenarioDatapoint.compartmentId.in_(compartments))
    if groups:
        query = query.where(db.ScenarioDatapoint.groupId.in_(groups))
    if percentiles:
        query = query.where(db.ScenarioDatapoint.percentile.in_(percentiles))
    
    with next(get_session()) as session:
        datapoints: List[db.ScenarioDatapoint] = session.exec(query).all()
    return [Infectiondata(
        date=point.timestamp.date(),
        node=str(point.nodeId),
        group=str(point.groupId),
        compartment=str(point.compartmentId),
        # aggregation=
        percentile=point.percentile,
        value=point.value
    ) for point in datapoints]
'''
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
                for parameter_value in query_results.parameter_values:
                    for group in parameter_value.groups:
                        grp = ModelParamaterValueEntry(
                            groupId=group.id,
                            valueMinInclusiv=group.value_min_inclusiv,
                            valueMaxExclusiv=group.value_max_exclusiv,
                        )
                        groups.append(grp)

                    for category in parameter_value.categories:
                        cat = ModelParamaterValueEntry(
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
'''