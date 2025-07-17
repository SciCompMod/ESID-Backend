# coding: utf-8

from typing import ClassVar, Dict, List, Tuple  # noqa: F401
from datetime import date, timedelta
from json import dumps
from pathlib import Path
from pydantic import Field, StrictBytes, StrictFloat, StrictInt, StrictStr
from typing import Any, Dict, List, Optional, Tuple, Union, Set
from typing_extensions import Annotated
from fastapi import HTTPException, UploadFile


class UtilsController:

    async def handle_case_data(
        self,
        file: UploadFile,
    ) -> None:
        """Validate the upladed file and forward it"""
        # Check if actually a csv file
        if not file or not file.filename.endswith('.csv'):
            raise HTTPException(
                status_code=400
            )
        return None
