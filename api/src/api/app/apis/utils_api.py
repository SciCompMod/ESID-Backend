# coding: utf-8

import logging
from typing import List  # noqa: F401
from datetime import date
from pydantic import Field, StrictStr
from typing import List, Optional
from typing_extensions import Annotated
from fastapi import (  # noqa: F401
    APIRouter,
    Body,
    File,
    Path,
    Query,
    Request,
    UploadFile,
)

from app.controller.utils_controller import UtilsController


router = APIRouter()
controller = UtilsController()

log = logging.getLogger('API.Utils')
logging.basicConfig(level=logging.INFO)

@router.post(
    "/utils/share/casedata",
    status_code=202,
    tags=["Utils"],
)
async def validate_and_forward_shared_case_data(
    file: UploadFile = File(None, description="csv file of case data to share with ESID")
) -> None:
    """Share Case Data with ESID."""
    log.info(f'POST /utils/caseshare received...')
    return await controller.handle_case_data(file)