# coding: utf-8

import logging
from typing import ClassVar, Dict, List, Tuple  # noqa: F401
from datetime import datetime
from json import dumps
from pathlib import Path
from pydantic import Field, StrictBytes, StrictFloat, StrictInt, StrictStr
from typing import Any, Dict, List, Optional, Tuple, Union, Set
from typing_extensions import Annotated
from fastapi import HTTPException, UploadFile
from starlette.datastructures import State
from app.models.user_detail import UserDetail
from core import config
from functools import lru_cache
from minio import Minio
import os
import requests

log = logging.getLogger('API.Utils')
logging.basicConfig(level=logging.INFO)

class UtilsController:

    async def handle_case_data_validation_upload(
        self,
        file: UploadFile,
        request_state: State,
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
        lha_id: str = request_state.realm
        # Get lha display name
        lha_name = next((realm['displayName'] for realm in get_realms() if realm['realm'] == lha_id), '')
        uploader: UserDetail = request_state.user

        meta = {
            'lha': {
                'id': lha_id,
                'name': lha_name,
            },
            'uploader': {
                'id': uploader.userId,
                'email': uploader.email,
                'roles': uploader.role,
            },
            'upload_timestamp': datetime.now().isoformat(),
        }

        object_path_in_bucket = os.path.join("arrivals", lha_id, file.filename)
        log.info(f'uploading \"{file.filename}\" into \"{object_path_in_bucket}\"')
        log.info(f'meta info: {meta}')
        
        client = create_minio_client()
        # go to end of stream to read size
        file.file.seek(0, os.SEEK_END)
        size = file.file.tell()
        # reset to start for upload
        file.file.seek(0, 0)
        try:
            result = client.put_object(
                bucket_name='private-lha-data',
                object_name=object_path_in_bucket,
                data=file.file,
                length=size
            )
            log.info(f'created: {result.object_name}, etag: {result.etag}, version: {result.version_id}')
        except Exception as ex:
            log.warning(f'Unable to upload file: {ex}')
            raise HTTPException(
                status_code=500,
                detail='An error occurred during file upload. Ceck the logs or contact an administrator.'
            )

        return None

@lru_cache
def get_realms() -> List[Any]:
    """
    Request realm list from IDP API
    """
    result_realms = requests.get(f'{str(config.IDP_API_URL)}/realms')
    if result_realms.status_code != 200:
        raise HTTPException(status_code=500, detail='IDP API unreachable to request realms')
    return result_realms.json()


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