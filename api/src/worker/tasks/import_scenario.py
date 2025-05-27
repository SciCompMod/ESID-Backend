from typing import List
from sqlmodel import select
from sqlalchemy.orm import selectinload

from app import celery_app, logger
from db import get_session
from db.models import (
    Scenario,
    Model,
    Group,
    Compartment,
    Node,
    ModelGroupLink,
    ModelCompartmentLink,
    NodeList,
    NodeListNodeLink,
)


class LookupObject:
    scenario: Scenario = None
    model: Model = None
    groups: List[Group] = []
    compartments: List[Compartment] = []
    nodes: List[Node]

    def __init__(self, scenarioId):
        with next(get_session()) as session:
            self.scenario = session.exec(
                # Find scenario by id
                select(Scenario).where(Scenario.id == scenarioId)
                    # Also load its model
                    .options(selectinload(Scenario.model))
                    # Also load the model's groups
                    .options(selectinload(Scenario.model).selectinload(Model.groups).selectinload(ModelGroupLink.group))
                    # Also load the model's compartments
                    .options(selectinload(Scenario.model).selectinload(Model.compartments).selectinload(ModelCompartmentLink.compartment))
                    # Also load the scenario's nodes
                    .options(selectinload(Scenario.nodelist).selectinload(NodeList.nodeLinks).selectinload(NodeListNodeLink.node))
            ).one_or_none()
            if not self.scenario:
                raise ValueError(f'Error loading Scenario for Lookup.')
        # populate shortcuts
        self.model = self.scenario.model
        self.groups = [groupLink.group for groupLink in self.model.groups]
        self.compartments = [compLink.compartment for compLink in self.model.compartments]
        self.nodes = [nodeLink.node for nodeLink in self.scenario.nodelist.nodeLinks]


CompartmentNames = {
    0: "MildInfections",
    1: "Hospitalized",
    2: "ICU",
    3: "Dead"
}


@celery_app.task(name='tasks.import_scenario', bind=True)
def test_worker(self, **kwargs):
    logger.info("Import Scenario Task started with:")
    logger.info(kwargs)

    # Get scenario infos from db
    try:
        info = LookupObject(kwargs['scenarioId'])
    except ValueError:
        logger.error("Scenario lookup failed.")

    return {
        'scenarioId': kwargs['scenarioId'],
        'taskId': self.request.id,
        'details': 'Import Successful',
        'scenario': info
    }
