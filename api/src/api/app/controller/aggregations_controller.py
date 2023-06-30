from app.models.new_aggregation import NewAggregation
from app.models.aggregation import Aggregation
from app.models.id import ID
from app.db import tasks
from uuid import uuid4
from app.models.error_models import IdNotAvailable


class AggregationsController:
    def create_new_aggregation(self, new_aggregation: NewAggregation):
        aggregation_id = str(uuid4())
        tasks.create_new_aggregation(aggregation_id, new_aggregation.name, new_aggregation.description, new_aggregation.tags)
        return ID(id=aggregation_id)

    def delete_aggregation_by_id(self, aggregation_id: str):
        try: 
            tasks.delete_aggregation_by_id(aggregation_id)
            return {"message": f"Aggregation with id: {aggregation_id} deleted"}
        except: 
            response = IdNotAvailable(message=f"Aggregation with Id {aggregation_id} not found.", status = 404)
            return response

    def get_aggregation_by_id(self, aggregation_id):
        aggregation_info = tasks.get_aggregation_by_id(aggregation_id)
        if aggregation_info:
            return aggregation_info
            
        else:
            response = IdNotAvailable(message=f"Aggregation with Id {aggregation_id} not found.", status = 404)
            return response

    def get_all_aggregations(self):
        aggregations = tasks.get_all_aggregations()
        try:
            aggregation_ids = [aggregation.id for aggregation in aggregations]
            return aggregation_ids
        except TypeError:
            response = IdNotAvailable(message="No aggregation definitions available", status=404)
            return response