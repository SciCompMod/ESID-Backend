from app.models.id import ID
from app.models.new_parameter_definition import NewParameterDefinition
from app.models.parameter_definition import ParameterDefinition
from uuid import uuid4
from app.db import tasks
from app.models.error_models import IdNotAvailable

class ParameterController:
    def create_parameter_definition(self, new_parameter_definition: NewParameterDefinition):
        parameter_definition_id = str(uuid4())
        tasks.create_new_parameter_definition(new_parameter_definition.name, new_parameter_definition.description, parameter_definition_id)
        return ID(id=parameter_definition_id)

    def delete_parameter_definition_by_id(self, parameter_id):
        tasks.delete_parameter_definition_by_id(parameter_id)
        response = IdNotAvailable(message=f"Node with id: {parameter_id} deleted", status=404)
        return response

    def get_parameter_definition_by_id(self, parameter_id):
        parameter_definition_info = tasks.get_parameter_definition_by_id(parameter_id)
        return ParameterDefinition(name=parameter_definition_info.name, description=parameter_definition_info.description, id=parameter_definition_info.id)

    def get_all_parameter_definitions(self):
        parameter_definitions = tasks.get_all_parameter_definitions()
        try:
            parameter_definition_ids = [parameter.id for parameter in parameter_definitions]
            return parameter_definition_ids
        except TypeError:
            response = IdNotAvailable(message="No parameter definitions available", status= 404)
            return response