from app.models.new_group import NewGroup
from app.models.group import Group
from app.models.id import ID
from uuid import uuid4
from app.db.tasks import create_new_group, get_all_group, get_group_by_id, delete_group_by_id
from app.models.error_models import IdNotAvailable


class GroupsController:
    def create_group(self, new_group: NewGroup):
        group_id = str(uuid4())
        create_new_group(new_group.name, new_group.description, new_group.category, id=group_id)
        return ID(id=group_id)
    
    def get_all_groups(self):
        groups = get_all_group()
        group_ids = []
        if groups:
            group_ids = [group.id for group in groups] 
        return group_ids

    def get_group_by_id(self, group_id):
        group = get_group_by_id(group_id)
        group_json_model = Group(name=group.name, description=group.description, category=group.category, id=group.id)
        return group_json_model
    
    def delete_group(self, group_id):
        if delete_group_by_id(group_id):
            return group_id
        response = IdNotAvailable(message=f"Group with id: {group_id} not found!",
                                  status=404)
        return response
    