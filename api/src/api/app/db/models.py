from datetime import datetime  # noqa: F401
from typing import List, Optional

from sqlmodel import Field, Relationship, SQLModel


class ModelGroupLink(SQLModel, table=True):
    group_id: Optional[str] = Field(
        default=None, foreign_key="group.id", primary_key=True, nullable=False
    )
    model_id: Optional[str] = Field(
        default=None, foreign_key="model.id", primary_key=True, nullable=False
    )


class ModelParameterLink(SQLModel, table=True):
    parameter_id: Optional[str] = Field(
        default=None,
        foreign_key="parameterdefinition.id",
        primary_key=True,
        nullable=False,
    )
    model_id: Optional[str] = Field(
        default=None, foreign_key="model.id", primary_key=True, nullable=False
    )


class Group(SQLModel, table=True):
    name: Optional[str] = Field(default=None)
    description: Optional[str] = Field(default=None)
    category: Optional[str] = Field(default=None)
    id: Optional[str] = Field(default=None, primary_key=True, nullable=False)
    models: List["Model"] = Relationship(
        back_populates="groups", link_model=ModelGroupLink
    )


class CompartmentAggregationLink(SQLModel, table=True):
    compartment_name: Optional[str] = Field(
        default=None, foreign_key="compartment.name", primary_key=True, nullable=False
    )
    compartment_aggr_name: Optional[str] = Field(
        default=None,
        foreign_key="compartmentaggregation.name",
        primary_key=True,
        nullable=False,
    )


class ModelCompartmentLink(SQLModel, table=True):
    compartment_name: Optional[str] = Field(
        default=None, foreign_key="compartment.name", primary_key=True, nullable=False
    )
    model_id: Optional[str] = Field(
        default=None, foreign_key="model.id", primary_key=True, nullable=False
    )


class Compartment(SQLModel, table=True):
    name: Optional[str] = Field(default=None, primary_key=True, nullable=False)
    description: Optional[str] = Field(default=None)
    tags: Optional[List[str]] = Field(default=None)
    models: List["Model"] = Relationship(
        back_populates="compartments", link_model=ModelCompartmentLink
    )
    compartment_aggregations: List["CompartmentAggregation"] = Relationship(
        back_populates="compartments", link_model=CompartmentAggregationLink
    )


class CompartmentAggregation(SQLModel, table=True):
    name: Optional[str] = Field(default=None, primary_key=True, nullable=False)
    description: Optional[str] = Field(default=None)
    tags: Optional[List[str]] = Field(default=None)
    compartments: List[Compartment] = Relationship(
        back_populates="compartment_aggregations", link_model=CompartmentAggregationLink
    )


class ScenarioInterventionLink(SQLModel, table=True):
    scenario_id: Optional[str] = Field(
        default=None, foreign_key="scenario.id", primary_key=True, nullable=False
    )
    intervention_id: Optional[str] = Field(
        default=None, foreign_key="intervention.id", primary_key=True, nullable=False
    )


class Intervention(SQLModel, table=True):
    name: Optional[str] = Field(default=None)
    description: Optional[str] = Field(default=None)
    id: Optional[str] = Field(default=None, primary_key=True, nullable=False)
    scenarios: List["Scenario"] = Relationship(
        back_populates="linked_interventions", link_model=ScenarioInterventionLink
    )


class ParameterDefinition(SQLModel, table=True):
    name: Optional[str] = Field(default=None)
    description: Optional[str] = Field(default=None)
    id: str = Field(default=None, primary_key=True, nullable=False)
    models: List["Model"] = Relationship(
        back_populates="parameter_definitions", link_model=ModelParameterLink
    )


class NodeNodeListLink(SQLModel, table=True):
    node_id: Optional[str] = Field(
        default=None, foreign_key="node.id", primary_key=True, nullable=False
    )
    nodelist_id: Optional[str] = Field(
        default=None, foreign_key="nodelist.id", primary_key=True, nullable=False
    )


class Node(SQLModel, table=True):
    name: Optional[str] = Field(default=None)
    description: Optional[str] = Field(default=None)
    id: Optional[str] = Field(default=None, primary_key=True, nullable=False)
    tags: Optional[str] = Field(default=None)
    node_lists: List["NodeList"] = Relationship(
        back_populates="nodes", link_model=NodeNodeListLink
    )


class NodeList(SQLModel, table=True):
    id: Optional[str] = Field(default=None, primary_key=True, nullable=False)
    name: Optional[str] = Field(default=None)
    description: Optional[str] = Field(default=None)
    nodes: List[Node] = Relationship(
        back_populates="node_lists", link_model=NodeNodeListLink
    )


class AggregationTagLink(SQLModel, table=True):
    tag_id: Optional[str] = Field(
        default=None, foreign_key="tag.id", primary_key=True, nullable=False
    )
    aggregation_id: Optional[str] = Field(
        default=None, foreign_key="aggregation.id", primary_key=True, nullable=False
    )


class ModelAggregationLink(SQLModel, table=True):
    model_id: Optional[str] = Field(
        default=None, foreign_key="model.id", primary_key=True, nullable=False
    )
    aggregation_id: Optional[str] = Field(
        default=None, foreign_key="aggregation.id", primary_key=True, nullable=False
    )


class Aggregation(SQLModel, table=True):
    id: Optional[str] = Field(default=None, primary_key=True, nullable=False)
    name: Optional[str] = Field(default=None)
    description: Optional[str] = Field(default=None)
    tags: List["Tag"] = Relationship(
        back_populates="aggregations", link_model=AggregationTagLink
    )
    models: List["Model"] = Relationship(
        back_populates="aggregations", link_model=ModelAggregationLink
    )


class Tag(SQLModel, table=True):
    id: Optional[str] = Field(default=None, primary_key=True, nullable=False)
    name: Optional[str] = Field(default=None)
    aggregations: List[Aggregation] = Relationship(
        back_populates="tags", link_model=AggregationTagLink
    )


class Model(SQLModel, table=True):
    id: Optional[str] = Field(default=None, primary_key=True, nullable=False)
    name: Optional[str] = Field(default=None)
    description: Optional[str] = Field(default=None)
    compartments: List[Compartment] = Relationship(
        back_populates="models", link_model=ModelCompartmentLink
    )
    groups: List[Group] = Relationship(
        back_populates="models", link_model=ModelGroupLink
    )
    aggregations: List[Aggregation] = Relationship(
        back_populates="models", link_model=ModelAggregationLink
    )
    parameter_definitions: List[ParameterDefinition] = Relationship(
        back_populates="models", link_model=ModelParameterLink
    )


class ScenarioParameterValueLink(SQLModel, table=True):
    scenario_id: Optional[str] = Field(
        default=None, foreign_key="scenario.id", primary_key=True, nullable=False
    )
    parameter_value_id: Optional[str] = Field(
        default=None, foreign_key="parametervalue.id", primary_key=True, nullable=False
    )


class ParameterValueGroupParameterValueRangeLink(SQLModel, table=True):
    parameter_value_id: Optional[str] = Field(
        default=None, foreign_key="parametervalue.id", primary_key=True, nullable=False
    )
    parameter_value_range_id: Optional[str] = Field(
        default=None,
        foreign_key="groupparametervaluerange.id",
        primary_key=True,
        nullable=False,
    )


class ParameterValueCategoryParameterValueRangeLink(SQLModel, table=True):
    parameter_value_id: Optional[str] = Field(
        default=None, foreign_key="parametervalue.id", primary_key=True, nullable=False
    )
    parameter_value_range_id: Optional[str] = Field(
        default=None,
        foreign_key="categoryparametervaluerange.id",
        primary_key=True,
        nullable=False,
    )


class GroupParameterValueRange(SQLModel, table=True):
    id: Optional[str] = Field(default=None, primary_key=True, nullable=False)
    value_min_inclusiv: Optional[float] = Field(default=None)
    value_max_exclusiv: Optional[float] = Field(default=None)
    parameter_values: List["ParameterValue"] = Relationship(
        back_populates="groups", link_model=ParameterValueGroupParameterValueRangeLink
    )


class CategoryParameterValueRange(SQLModel, table=True):
    id: Optional[str] = Field(default=None, primary_key=True, nullable=False)
    value_min_inclusiv: Optional[float] = Field(default=None)
    value_max_exclusiv: Optional[float] = Field(default=None)
    parameter_values: List["ParameterValue"] = Relationship(
        back_populates="categories",
        link_model=ParameterValueCategoryParameterValueRangeLink,
    )


class ParameterValue(SQLModel, table=True):
    id: Optional[str] = Field(default=None, primary_key=True, nullable=False)
    groups: List["GroupParameterValueRange"] = Relationship(
        back_populates="parameter_values",
        link_model=ParameterValueGroupParameterValueRangeLink,
    )
    categories: List["CategoryParameterValueRange"] = Relationship(
        back_populates="parameter_values",
        link_model=ParameterValueCategoryParameterValueRangeLink,
    )
    scenarios: List["Scenario"] = Relationship(
        back_populates="parameter_values", link_model=ScenarioParameterValueLink
    )


class Scenario(SQLModel, table=True):
    id: Optional[str] = Field(default=None, primary_key=True, nullable=False)
    name: Optional[str] = Field(default=None)
    description: Optional[str] = Field(default=None)
    model_id: Optional[str] = Field(foreign_key="model.id")
    node_list_id: Optional[str] = Field(foreign_key="nodelist.id")
    linked_interventions: List["Intervention"] = Relationship(
        back_populates="scenarios", link_model=ScenarioInterventionLink
    )
    parameter_values: List["ParameterValue"] = Relationship(
        back_populates="scenarios", link_model=ScenarioParameterValueLink
    )


class Migration(SQLModel, table=True):
    id: Optional[str] = Field(default=None, primary_key=True, nullable=False)
    start_node: Optional[str] = Field(foreign_key="node.id")
    end_node: Optional[str] = Field(foreign_key="node.id")
    timestamp: Optional[datetime] = Field(default=None)
    value: Optional[int] = Field(default=None)
    compartment_name: Optional[str] = Field(
        default=None, foreign_key="compartment.name", primary_key=True, nullable=False
    )
    group_id: Optional[str] = Field(
        default=None, foreign_key="group.id", primary_key=True, nullable=False
    )
    run_id: Optional[str] = Field(
        default=None,
        foreign_key="runsimulations.run_id",
        primary_key=True,
        nullable=False,
    )
    scenario_id: Optional[str] = Field(foreign_key="scenario.id")


class RunSimulations(SQLModel, table=True):
    scenario_id: Optional[str] = Field(foreign_key="scenario.id")
    run_id: Optional[str] = Field(default=None, primary_key=True, nullable=False)


class InfectionData(SQLModel, table=True):
    id: Optional[str] = Field(default=None, primary_key=True, nullable=False)
    timestamp: Optional[str] = Field(default=None)
    node: Optional[str] = Field(foreign_key="node.id")
    value: Optional[float] = Field(default=None)


class Cell(SQLModel, table=True):
    name: Optional[str] = Field(default=None)
    description: Optional[str] = Field(default=None)
    id: Optional[str] = Field(default=None, primary_key=True, nullable=False)
    tags: Optional[str] = Field(default=None)


class Movements(SQLModel, table=True):
    id: Optional[str] = Field(default=None, primary_key=True, nullable=False)
    start_cell: Optional[str] = Field(foreign_key="cell.id")
    end_cell: Optional[str] = Field(foreign_key="cell.id")
    timestamp: Optional[datetime] = Field(default=None)
    value: Optional[int] = Field(default=None)
    compartment_name: Optional[str] = Field(
        default=None, foreign_key="compartment.name", primary_key=True, nullable=False
    )
    group_id: Optional[str] = Field(
        default=None, foreign_key="group.id", primary_key=True, nullable=False
    )
    run_id: Optional[str] = Field(
        default=None,
        foreign_key="runsimulations.run_id",
        primary_key=True,
        nullable=False,
    )
    scenario_id: Optional[str] = Field(foreign_key="scenario.id")
    travel_mode: Optional[str] = Field(default=None)
    activity: Optional[str] = Field(default=None)
    travel_time: Optional[datetime] = Field(default=None)
