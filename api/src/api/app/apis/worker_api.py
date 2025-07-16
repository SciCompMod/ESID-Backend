# coding: utf-8

import json
import logging
from typing import Dict, List  # noqa: F401
from datetime import date
from uuid import UUID
from pydantic import Field, StrictBytes, StrictFloat, StrictInt, StrictStr
from typing import Any, Dict, List, Optional, Tuple, Union
from typing_extensions import Annotated
from fastapi import (  # noqa: F401
    APIRouter,
    Body,
    Cookie,
    Depends,
    File,
    Form,
    Header,
    HTTPException,
    Path,
    Query,
    Security,
    status,
    UploadFile,
)
from fastapi.responses import JSONResponse
from celery.result import AsyncResult
from app import celery_app

from app.models.extra_models import TokenModel  # noqa: F401
from app.models.error import Error
from app.models.id import ID
from app.models.infectiondata import Infectiondata
from app.models.reduced_scenario import ReducedScenario
from app.models.scenario import Scenario

from app.controller.scenario_controller import ScenarioController


router = APIRouter()
controller = ScenarioController()

log = logging.getLogger('API.Worker')
logging.basicConfig(level=logging.INFO)

class CustomEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, UUID):
            # if the obj is uuid, we simply return the value of uuid
            return o.hex
        if isinstance(o, date):
            return o.isoformat()
        return json.JSONEncoder.default(self, o)

@router.get(
    "/worker/task/{taskId}",
    tags=["Worker"]
)
async def get_task_info(
  taskId: StrictStr = Path(..., description="UUID of the task")
) -> JSONResponse:
  """Get info on a task"""
  result = AsyncResult(taskId, app=celery_app)
  return JSONResponse(
    content={
      'status': json.loads(json.dumps(result.status, cls=CustomEncoder)),
      'result': json.loads(json.dumps(result.result, cls=CustomEncoder))
    },
    status_code=200
  )