# Entity-Relationship-Diagram

```mermaid
erDiagram
    Scenario {
        string id PK
        string name "*"
        string description
        string startDate "*"
        string endDate "*"
        Model modelId FK "* UUID of the used model"
        NodeList nodeListId FK "* UUID of the Nodelist used in the scenario"
        ParameterValue[] modelParameters FK "* List of Parameter UUIDs & their values for each Group UUID"
        InterventionImplementation[] linkedInterventions FK "List of InterventionTemplate UUIDs and the implementation values"
        string timestampSubmitted
        string timestampSimulated
    }

    Scenario }o..|| Model: ""
    Scenario ||--|{ _ParameterValue_: ""
    Scenario }o..|| NodeList: ""
    Scenario ||--|{ _InterventionImplementation_: ""

    Model {
        string id PK
        string name "*"
        string description
        Compartment[] compartments FK "* UUIDs of compartments the model has"
        Group[] groups FK "* UUIDs of groups the model has"
        ParameterDefinition[] parameterDefinitions FK "* UUIDs of parameters available with the model"
    }

    _ParameterValue_ {
        Scenario scenarioId PK "UUID of the scenario"
        ParameterDefinition definitionId PK "UUID of the definition"
        ParameterValueRange[] values "*"
    }

    _ParameterValueEntry_ {
        string paramterId PK "UUID of the ParameterValue this belongs to"
        string groupId PK "UUID of the group this value is for"
        number valueMin "*"
        number valueMax "*"
    }

    _ParameterValue_ ||--|{ _ParameterValueEntry_: ""
    _ParameterValueEntry_ }o--|| Group: ""
    _ParameterValue_ }o--|| ParameterDefinition: ""

    ParameterDefinition {
        string id PK
        string name "*"
        string description
    }
    
    ParameterDefinition }|..o{ Model: ""

    NodeList{
        string id PK
        string name "*"
        string description
        Node[] nodeIds FK "*"
    }

    NodeList }o..|{ Node: ""

    Node {
        string id PK
        string nuts "*"
        string name "*"
    }

    _InterventionImplementation_ }o--|| InterventionTemplate: ""

    _InterventionImplementation_ {
        string interventionId FK
        string startDate
        string endDate
        number coefficient
    }

    InterventionTemplate {
        string id PK
        string name "*"
        string description
        string[] tags "tags used for search & filtering"
    }

    Group {
        string id PK
        string name "*"
        string description
        string category "*"
    }

    Group }|..o{ Model: ""

    Compartment {
        string id PK
        string name "*"
        string description
        string[] tags "tags used of aggregation"
    }

    Model }o..|{ Compartment: ""

    ScenarioDatapoint{
        string id PK
        string scenarioId FK
        string timestamp
        string nodeId FK
        string group FK
        string compartment FK
        string percentile
        string value
    }
    ScenarioDatapoint }|--|| Scenario: ""
    ScenarioDatapoint }|--|| Node: ""
    ScenarioDatapoint }|--|| Group: ""
    ScenarioDatapoint }|--|| Compartment: ""
    ```