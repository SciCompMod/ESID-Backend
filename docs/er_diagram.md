# Entity-Relationship-Diagram

```mermaid
erDiagram
    Scenario {
        string id PK
        string name
        string description
        string startDate
        string endDate
        Model modelId FK "UUID of the used model"
        ParameterValue[] modelParameters FK "List of Parameter UUIDs & their values for each Group UUID"
        NodeList nodeListId FK "UUID of the Nodelist used in the scenario"
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
        string name
        string description
        Compartment[] compartments FK "UUIDs of compartments the model has"
        Group[] groups FK "UUIDs of groups the model has"
        ParameterDefinition[] parameterDefinitions FK "UUIDs of parameters available with the model"
    }

    _ParameterValue_ {
        ParameterDefinition id FK "UUID of the definition"
        ParameterValueRange[] values FK "each item contains group uuid and values"
    }

    _ParameterValue_ }o--|{ Group: ""
    _ParameterValue_ }o--|| ParameterDefinition: ""

    ParameterDefinition {
        string id PK
        string name
        string description
    }
    
    ParameterDefinition }|..o{ Model: ""

    NodeList{
        string id PK
        string name
        string description
        Node[] nodeIds FK
    }

    NodeList }o..|{ Node: ""

    Node {
        string id PK
        string nuts
        string name
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
        string name
        string description
        string[] tags "tags used for search & filtering"
    }

    Group {
        string id PK
        string name
        string description
        string category
    }

    Group }|..o{ Model: ""

    Compartment {
        string id PK
        string name
        string description
        string[] tags "tags used of aggregation"
    }

    Model }o..|{ Compartment: ""
    ```