# coding: utf-8

import logging
from typing import ClassVar, Dict, List, Tuple  # noqa: F401
from datetime import date, timedelta
from json import dumps
from pathlib import Path
from pydantic import Field, StrictBytes, StrictFloat, StrictInt, StrictStr
from typing import Any, Dict, List, Optional, Tuple, Union, Set
from typing_extensions import Annotated
from fastapi import HTTPException, UploadFile
from core import config
from functools import lru_cache
from minio import Minio
from os import path

log = logging.getLogger('API.Utils')
logging.basicConfig(level=logging.INFO)

class UtilsController:

    @lru_cache
    def create_minio_client() -> Minio:
        """
        Create a Minio client to upload to a bucket
        """
        client = Minio(
            endpoint=str(config.UPLOAD_FORWARD_ENDPOINT),
            access_key=str(config.UPLOAD_FORWARD_ACCESS_KEY),
            secret_key=str(config.UPLOAD_FORWARD_SECRET_KEY),
        )
        return client
    

    async def handle_case_data_validation_upload(
        self,
        file: UploadFile,
    ) -> None:
        """Validate the upladed file and forward it"""
        # Check if actually a csv file
        if not file or not file.filename or not file.filename.lower().endswith('.csv'):
            raise HTTPException(
                status_code=400,
                detail='No CSV file sent'
            )
        # Check mime type
        valid_content_types = ['text/csv', 'application/vnd.ms-excel']
        if file.content_type not in valid_content_types:
            raise HTTPException(
                status_code=400,
                detail=f"File has the wrong content type. Accepts {valid_content_types} but got '{file.content_type}'"
            )
        # Check first line
        line = file.file.readline().decode(encoding='utf-8')
        num_cols = len(line.split(';'))  # This assumes ';' is always used as separator
        if num_cols != 76:  # This is also assumes the file always hass this magic number of columns
            raise HTTPException(
                status_code=400,
                detail=f"File has the wrong amount of columns. Needs 76 but has '{num_cols}'"
            )
        
        # Validation successful, upload to minio bucket
        object_path_in_bucket = path.join("arrivals", "<lha_id>", file.filename)

        return None
