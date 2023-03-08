from app.models.new_node import NewNode
from app.models.new_node_list import NewNodeList
from app.models.node_list import NodeList
from app.models.node import Node
from app.models.id import ID
from uuid import uuid4
from app.db import tasks
# from app.db.tasks import (create_new_node, get_all_nodes, _get_node_by_id, 
# _delete_node_by_id)


class NodesController:
    def create_new_node(self, new_node: NewNode):
        node_id = str(uuid4())
        tasks.create_new_node(new_node.name, new_node.description, node_id)
        return ID(id=node_id)

    def get_all_nodes(self):
        nodes = tasks.get_all_nodes()
        node_ids = []
        if nodes:
            node_ids = [node.id for node in nodes] 
        return node_ids

    def get_node_by_id(self, node_id):
        node = tasks._get_node_by_id(node_id)
        node_json_model = Node(name=node.name, description=node.description, id=node.id)
        return node_json_model

    def delete_node_by_id(self, node_id):
        if tasks._delete_node_by_id(node_id):
            return node_id
        return {"message": f"Node with id: {node_id} not found!", "status": 404}

    
    def create_new_nodelist(self, new_nodelist: NewNodeList):
        nodelist_id = str(uuid4())
        try:
            tasks.create_node_list(new_nodelist.name, new_nodelist.description, new_nodelist.node_ids[0], id=nodelist_id)
            return ID(id=nodelist_id)
        except ValueError as e:
            return {'status': 404, "message": str(e)}

    def get_all_nodelists(self):
        nodeslists = tasks.get_all_nodelists()
        nodelist_ids = []
        if nodeslists:
            nodelist_ids = [nodelist.id for nodelist in nodeslists] 
        return nodelist_ids

    def get_nodelist_by_id(self, nodelist_id):
        nodelist = tasks._get_nodelist_by_id(nodelist_id)
        if nodelist:
            return nodelist
        return {"status": 404, "message": f"NodeList with id '{nodelist_id}' not found!"}

    def delete_nodelist_by_id(self, nodelist_id):
        if tasks._delete_nodelist_by_id(nodelist_id):
            return nodelist_id
        return {"message": f"Node with id: {nodelist_id} not found!", "status": 404}