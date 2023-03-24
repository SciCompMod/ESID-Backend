from app.models.model import Model
from app.models.new_model import NewModel
from app.models.new_node_list import NewNodeList
from app.models.node import Node
from app.models.id import ID
from uuid import uuid4
from app.db import tasks
from app.db.models import Compartment, Aggregation
from app.models.compartment import Compartment as Model_Compartment
from app.models.group import Group as Model_Group
from app.models.parameter_definition import ParameterDefinition as Model_ParameterDefinition
from app.db.models import Tag
# from app.db.tasks import (create_new_node, get_all_nodes, _get_node_by_id,
# _delete_node_by_id)
from app.models.error_models import IdNotAvailable


class ModelsController:
    def create_new_model(self, new_model: NewModel):
        model_id = str(uuid4())
        compartments = []
        for comp in new_model.compartments:
            compartments.append(Compartment(
                name=comp.name, description=comp.description, tags=comp.tags))

        tasks.create_new_model(model_id, new_model.name, new_model.description, compartments,
                               new_model.groups, new_model.aggregations, new_model.parameter_definitions)
        return ID(id=model_id)

    def get_all_models(self):
        models = tasks.get_all_models()
        model_ids = []
        if models:
            model_ids = [node.id for node in models]
        return model_ids

    def get_model_by_id(self, model_id):
        model = tasks._get_model_by_id(model_id)
        
        return model

    def delete_model_by_id(self, model_id):
        if tasks._delete_model_by_id(model_id):
            return model_id
        response = IdNotAvailable(message = f"Node with id: {model_id} not found!", status= 404)
        return response
