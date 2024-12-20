import uuid
from datetime import date, datetime  # noqa: F401
from typing import List, Optional

from sqlmodel import Field, Relationship, SQLModel, ARRAY, Float, Column
from sqlalchemy import ForeignKeyConstraint, PrimaryKeyConstraint


class Scenario(SQLModel, table=True):
    id: Optional[uuid.UUID] = Field(default_factory=uuid.uuid4, primary_key=True, nullable=False)
    name: Optional[str] = Field(nullable=False)
    description: Optional[str] = Field(default=None, nullable=True)
    
    startDate: Optional[date] = Field(nullable=False)
    endDate: Optional[date] = Field(nullable=False)
    
    modelId: Optional[uuid.UUID] = Field(foreign_key="model.id", nullable=False)
    model: "Model" = Relationship(back_populates="scenarios")

    nodeListId: Optional[uuid.UUID] = Field(foreign_key="nodelist.id", nullable=False)
    nodelist: "NodeList" = Relationship(back_populates="scenarios")

    modelParameters: List["ParameterValue"] = Relationship(back_populates="scenario", cascade_delete=True)
    linkedInterventions: List["InterventionImplementation"] = Relationship(back_populates="scenario", cascade_delete=True)

    percentiles: Optional[str] = Field(default='50', nullable=False)

    timestampSubmitted: Optional[datetime] = Field(default=None, nullable=True)
    timestampSimulated: Optional[datetime] = Field(default=None, nullable=True)


class ParameterDefinition(SQLModel, table=True):
    id: Optional[uuid.UUID] = Field(default_factory=uuid.uuid4, primary_key=True, nullable=False)
    name: Optional[str] = Field(nullable=False)
    description: Optional[str] = Field(default=None, nullable=True)

    scenarioLinks: List["ParameterValue"] = Relationship(back_populates="parameter")
    modelLinks: List["ModelParameterDefinitionLink"] = Relationship(back_populates="parameter")


class ParameterValue(SQLModel, table=True):
    # Composite primary key
    __tableargs__ = (
        PrimaryKeyConstraint('scenarioId', 'definitionId'),
    )
    scenarioId: Optional[uuid.UUID] = Field(default=None, nullable=False, primary_key=True, foreign_key="scenario.id") # cascade delete this if Scenario is deleted
    definitionId: Optional[uuid.UUID] = Field(default=None, nullable=False, primary_key=True, foreign_key="parameterdefinition.id") # Cannot delete ParameterDefinition if used in Scenario
    values: List["ParameterValueEntry"] = Relationship(back_populates="parameterValueLink", cascade_delete=True)

    scenario: "Scenario" = Relationship(back_populates="modelParameters")
    parameter: "ParameterDefinition" = Relationship(back_populates="scenarioLinks")


class ParameterValueEntry(SQLModel, table=True):
    # Composite foreign key (for Relatioship with Parameter Value)
    __table_args__ = (
        ForeignKeyConstraint(
            ['parameterValueIdScenario', 'parameterValueIdDefinition'],
            ['parametervalue.scenarioId', 'parametervalue.definitionId']
        ),
    )
    id: Optional[uuid.UUID] = Field(default_factory=uuid.uuid4, primary_key=True, nullable=False)
    parameterValueIdScenario: Optional[uuid.UUID] = Field(default=None, nullable=False)    # Cascade delete this if Parameter Value -> Scenario is deleted
    parameterValueIdDefinition: Optional[uuid.UUID] = Field(default=None, nullable=False)  # -- " --
    parameterValueLink: ParameterValue = Relationship(back_populates="values")

    groupId: Optional[uuid.UUID] = Field(default=None, nullable=False, foreign_key="group.id") # Cannot delete Group if used in Parameter Value -> Scenario
    group: "Group" = Relationship(back_populates="parameterValueEntries")

    valueMin: Optional[float] = Field(default=None, nullable=False)
    valueMax: Optional[float] = Field(default=None, nullable=False)


class Group(SQLModel, table=True):
    id: Optional[uuid.UUID] = Field(default_factory=uuid.uuid4, primary_key=True, nullable=False)
    name: Optional[str] = Field(default=None, nullable=False)
    description: Optional[str] = Field(default=None, nullable=True)
    category: Optional[str] = Field(default=None, nullable=False)

    parameterValueEntries: List[ParameterValueEntry] = Relationship(back_populates="group")
    modelLinks: List["ModelGroupLink"] = Relationship(back_populates="group")


class Compartment(SQLModel, table=True):
    id: Optional[uuid.UUID] = Field(default_factory=uuid.uuid4, primary_key=True, nullable=False)
    name: Optional[str] = Field(default=None, nullable=False)
    description: Optional[str] = Field(default=None, nullable=True)
    tags: Optional[str] = Field(default=None, nullable=True)

    modelLinks: List["ModelCompartmentLink"] = Relationship(back_populates="compartment")


class Model(SQLModel, table=True):
    id: Optional[uuid.UUID] = Field(default_factory=uuid.uuid4, primary_key=True, nullable=False)
    name: Optional[str] = Field(default=None, nullable=False)
    description: Optional[str] = Field(default=None, nullable=True)
    
    compartments: List["ModelCompartmentLink"] = Relationship(back_populates="model", cascade_delete=True)
    groups: List["ModelGroupLink"] = Relationship(back_populates="model", cascade_delete=True)
    parameterDefinitions: List["ModelParameterDefinitionLink"] = Relationship(back_populates="model", cascade_delete=True)

    scenarios: List["Scenario"] = Relationship(back_populates="model")


class ModelCompartmentLink(SQLModel, table=True):
    # Composite primary key
    __tableargs__ = (
        PrimaryKeyConstraint('modelId', 'compartmentId'),
    )
    modelId: Optional[uuid.UUID] = Field(default=None, nullable=False, primary_key=True, foreign_key="model.id") # Cascade delete this if Model is deleted
    compartmentId: Optional[uuid.UUID] = Field(default=None, nullable=False, primary_key=True, foreign_key="compartment.id") # Cannot delete Compartment if used in Model

    model: "Model" = Relationship(back_populates="compartments")
    compartment: "Compartment" = Relationship(back_populates="modelLinks")


class ModelParameterDefinitionLink(SQLModel, table=True):
    # Composite primary key
    __tableargs__ = (
        PrimaryKeyConstraint('modelId', 'parameterId'),
    )
    modelId: Optional[uuid.UUID] = Field(default=None, nullable=False, primary_key=True, foreign_key="model.id") # Cascade delete this if Model is deleted
    parameterId: Optional[uuid.UUID] = Field(default=None, nullable=False, primary_key=True, foreign_key="parameterdefinition.id") # Cannot delete ParameterDefinition if used in Model

    model: "Model" = Relationship(back_populates="parameterDefinitions")
    parameter: "ParameterDefinition" = Relationship(back_populates="modelLinks")


class ModelGroupLink(SQLModel, table=True):
    # Composite primary key
    __tableargs__ = (
        PrimaryKeyConstraint('modelId', 'groupId'),
    )
    modelId: Optional[uuid.UUID] = Field(default=None, nullable=False, primary_key=True, foreign_key="model.id") # Cascade delete this if Model is deleted
    groupId: Optional[uuid.UUID] = Field(default=None, nullable=False, primary_key=True, foreign_key="group.id") # Cannot delete Group if used in Model

    model: "Model" = Relationship(back_populates="groups")
    group: "Group" = Relationship(back_populates="modelLinks")


class InterventionTemplate(SQLModel, table=True):
    id: Optional[uuid.UUID] = Field(default_factory=uuid.uuid4, primary_key=True, nullable=False)
    name: Optional[str] = Field(default=None, nullable=False)
    description: Optional[str] = Field(default=None, nullable=True)
    tags: Optional[str] = Field(default=None, nullable=True)

    implementations: List["InterventionImplementation"] = Relationship(back_populates="template")


class InterventionImplementation(SQLModel, table=True):
    # Composite primary key
    __tableargs__ = (
        PrimaryKeyConstraint('scenarioId', 'interventionId'),
    )
    scenarioId: Optional[uuid.UUID] = Field(default=None, nullable=False, primary_key=True, foreign_key="scenario.id") # Cascade delete this if Scenario is deleted
    interventionId: Optional[uuid.UUID] = Field(default=None, nullable=False, primary_key=True, foreign_key="interventiontemplate.id") # Cannot delete InterventionTemplate if used in Scenario
    startDate: Optional[date] = Field(default=None, nullable=False)
    endDate: Optional[date] = Field(default=None, nullable=False)
    coefficient: Optional[float] = Field(default=None, nullable=False)

    scenario: "Scenario" = Relationship(back_populates="linkedInterventions")
    template: "InterventionTemplate" = Relationship(back_populates="implementations")


class Node(SQLModel, table=True):
    id: Optional[uuid.UUID] = Field(default_factory=uuid.uuid4, primary_key=True, nullable=False) # TODO: do we need uuid? are nuts unique?
    nuts: Optional[str] = Field(default=None, nullable=False)
    name: Optional[str] = Field(default=None, nullable=False)

    nodelistLinks: List["NodeListNodeLink"] = Relationship(back_populates="node")


class NodeList(SQLModel, table=True):
    id: Optional[uuid.UUID] = Field(default_factory=uuid.uuid4, primary_key=True, nullable=False)
    name: Optional[str] = Field(default=None, nullable=False)
    description: Optional[str] = Field(default=None, nullable=True)

    nodeLinks: List["NodeListNodeLink"] = Relationship(back_populates="list", cascade_delete=True)
    scenarios: List["Scenario"] = Relationship(back_populates="nodelist")


class NodeListNodeLink(SQLModel, table=True):
    # Composite primary key
    __tableargs__ = (
        PrimaryKeyConstraint('nodeId', 'listId'),
    )
    nodeId: Optional[uuid.UUID] = Field(default=None, nullable=False, primary_key=True, foreign_key="node.id") # Cannot delete Node if used in NodeList 
    listId: Optional[uuid.UUID] = Field(default=None, nullable=False, primary_key=True, foreign_key="nodelist.id") # Cascade delete this if NodeList is deleted

    node: "Node" = Relationship(back_populates="nodelistLinks")
    list: "NodeList" = Relationship(back_populates="nodeLinks")


class ScenarioDatapoint(SQLModel, table=True):
    id: Optional[uuid.UUID] = Field(default_factory=uuid.uuid4, primary_key=True, nullable=False)
    scenarioId: Optional[uuid.UUID] = Field(default=None, nullable=False, foreign_key="scenario.id")
    timestamp: Optional[datetime] = Field(default=None, nullable=False) # TODO: date enough?
    nodeId: Optional[uuid.UUID] = Field(default=None, nullable=False, foreign_key="node.id")
    groupId: Optional[uuid.UUID] = Field(default=None, nullable=False, foreign_key="group.id")
    compartmentId: Optional[uuid.UUID] = Field(default=None, nullable=False, foreign_key="compartment.id")
    percentile: Optional[int] = Field(default=None, nullable=False)
    value: Optional[float] = Field(default=None, nullable=False)
