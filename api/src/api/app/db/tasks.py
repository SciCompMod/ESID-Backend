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
from sqlalchemy import delete
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

def group_get_all() -> List[Group]:
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

def node_get_by_list(id: StrictStr) -> List[Node]:
    query = select(db.Node).where(db.Node.id.in_(select(db.NodeListNodeLink.nodeId).where(db.NodeListNodeLink.listId == id)))
    with next(get_session()) as session:
        nodes: List[Node] = session.exec(query).all()
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

def nodelist_get_by_id(id: StrictStr) -> NodeListWithNodes:
    query = select(db.NodeList).where(db.NodeList.id == id).options(selectinload(db.NodeList.nodeLinks).selectinload(db.NodeListNodeLink.node))
    with next(get_session()) as session:
        nodelist: db.NodeList = session.exec(query).one_or_none()
        if not nodelist:
            raise HTTPException(status_code=404, detail='A nodelist with this ID does not exist')
        nodeIDs: List[Node] = [Node(
            id=str(link.node.id),
            nuts=link.node.nuts,
            name=link.node.name
            )for link in nodelist.nodeLinks]
    return NodeListWithNodes(
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
        percentiles=','.join([str(perc) for perc in scenario.percentiles]) if scenario.percentiles else '50',
        timestampSubmitted=datetime.now(),
        timestampSimulated=None,
        creatorUserId=scenario.creator_user_id,
        creatorOrgId=scenario.creator_org_id
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
        # validate interventions (if there are any)
        if scenario.linked_interventions:
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
        # Intervention Implementation Links (if there are interventions)
        if scenario.linked_interventions:
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
        creator_user_id=str(scenario.creatorUserId),
        creator_org_id=scenario.creatorOrgId
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
        percentiles=[int(perc) for perc in sc.percentiles.split(',')],
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
        
        # Delete Intervention Implementations for this scenario
        interventions: List[db.InterventionImplementation] = session.exec(
            select(db.InterventionImplementation).where(db.InterventionImplementation.scenarioId == id)
        ).all()
        for intervention in interventions:
            session.delete(intervention)
        # Delete Parameter Values for this scenario
        parameters: List[db.ParameterValue] = session.exec(
            select(db.ParameterValue).where(db.ParameterValue.scenarioId == id)
        ).all()
        for param in parameters:
            session.delete(param)
        # Delete Parameter Value Entries tied to the parameter values (also found by scenario id due to composite key)
        entries: List[db.ParameterValueEntry] = session.exec(
            select(db.ParameterValueEntry).where(db.ParameterValueEntry.parameterValueIdScenario == id)
        ).all()
        for entry in entries:
            session.delete(entry)
        # Delete all datapoints associated to the scenario
        data: List[db.ScenarioDatapoint] = session.exec(
            select(db.ScenarioDatapoint).where(db.ScenarioDatapoint.scenarioId == id)
        ).all()
        for point in data:
            session.delete(point)

        # Finally delete scenario
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

def datapoint_update_all_by_scenario(
    scenarioId: StrictStr,
    datapoints: List[Infectiondata]
) -> None:
    query = select(db.Scenario).where(db.Scenario.id == scenarioId)
    with next(get_session()) as session:
        # Delete old datapoints
        session.exec(
            # SQLAlchemy Statement to delete all records without loading all found entries into memory
            delete(db.ScenarioDatapoint).where(db.ScenarioDatapoint.scenarioId == scenarioId)
        )
        # Add new datapoints
        session.add_all([db.ScenarioDatapoint(
            scenarioId=scenarioId,
            timestamp=datetime.combine(dp.var_date, time.min),
            nodeId=dp.node,
            groupId=dp.group,
            compartmentId=dp.compartment,
            percentile=dp.percentile,
            value=dp.value
        ) for dp in datapoints])
        # Update timestampSimulated
        scenario: db.Scenario = session.exec(query).one_or_none()
        scenario.timestampSimulated = datetime.now()
        session.add(scenario)
        session.commit()
    return
