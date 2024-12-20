import csv
import datetime
from enum import Enum
from io import StringIO
from typing import List, Optional

from fastapi import APIRouter, UploadFile, File, Form, Depends
from pydantic import BaseModel

from app.api.processes.load_schedule import masters_load_schedule_into_db, publishing_load_schedule_into_db
from app.api.utils import get_user

router = APIRouter(prefix='/v1/import', tags=['load'])


class MasterRow(BaseModel):
    artist: str
    track: str
    isrc: Optional[str] = None


class PublishingRow(BaseModel):
    writer: str
    alias: str
    ipi: Optional[str] = None
    title: str
    iswc: Optional[str] = None
    ownershippcnt: float


class MasterLoad(BaseModel):
    deal_name: str
    completed_date: datetime.date
    copyright: str
    business_entity: str
    third_party_admin_expiry: datetime.date
    is_passive: bool
    is_bfm_owned: bool
    rights_type: List[str]
    rows: List[MasterRow | PublishingRow]


def attach_metadata(_dict: dict, **kwargs):
    _dict.update(kwargs)
    return _dict


def read_csv_file(file_content, **kwargs):
    csv_string = StringIO(file_content)
    reader = csv.reader(csv_string)
    file_headers = next(reader)
    return map(lambda x: attach_metadata(dict(zip(file_headers, x)), **kwargs), reader)


def validate_copyright_type(copyright: str):
    if copyright.lower() not in ['masters', 'publishing']:
        raise ValueError(f'Rights type not supported: {copyright}. Use "masters" or "publishing"')
    return copyright.lower()


def run_import(rights_type: str, data: list, rms_user: str):
    if rights_type == 'recording':
        return masters_load_schedule_into_db(data, rms_user)
    elif rights_type == 'publishing':
        return publishing_load_schedule_into_db(data, rms_user)


class PublishingRightsType(Enum):
    WRITER_SHARE = 'writer_share'
    PUBLISHER_SHARE = 'publisher_share'
    ADMINISTRATION = 'administration'


class RecordingRightsType(Enum):
    RECORDING_OWNERSHIP = 'recording_ownership'
    DISTRIBUTION = 'distribution'
    NEIGHBORING_RIGHTS = 'neighboring_rights'
    ADMINISTRATION = 'administration'


class Exclusivity(Enum):
    EXCLUSIVE = 'exclusive'
    NON_EXCLUSIVE = 'non_exclusive'


class RightsScope(Enum):
    WORLDWIDE = 'worldwide'
    REGIONAL = 'regional'
    NATIONAL = 'national'
    SPECIFIC_MEDIA = 'specific_media'


@router.post('/schedule/publishing')
async def load_file(file: UploadFile = File(),
                    deal_id: str = Form(),  # TODO: Update
                    right_type: PublishingRightsType = Form(),
                    is_controlled: bool = Form(),
                    territories: List[str] = Form(...),
                    calculate_mech_share: bool = Form(False),
                    reversion_date: datetime.date = Form(None),
                    rms_user=Depends(get_user)):
    main_copyright_type = 'publishing'
    file_content = await file.read()
    file_content_string = file_content.decode('utf-8-sig')
    data = read_csv_file(file_content_string,
                         deal_id=deal_id,
                         right_type=right_type.value,
                         territories=territories,
                         calculate_mech_share=calculate_mech_share,
                         is_controlled=is_controlled,
                         reversion_date=reversion_date
                         )
    res = run_import(main_copyright_type, data, rms_user)
    return 1


@router.post('/schedule/recordings')
async def load_file(file: UploadFile = File(),
                    deal_id: str = Form(),  # TODO: Update
                    right_type: RecordingRightsType = Form(),
                    is_controlled: bool = Form(),
                    territories: List[str] = Form(...),
                    reversion_date: datetime.date = Form(None),
                    rms_user=Depends(get_user)):
    main_copyright_type = 'recording'
    file_content = await file.read()
    file_content_string = file_content.decode('utf-8-sig')

    data = read_csv_file(file_content_string,
                         deal_id=deal_id,
                         right_type=right_type.value,
                         is_controlled=is_controlled,
                         territories=territories,
                         reversion_date=reversion_date)
    res = run_import(main_copyright_type, data, rms_user)
    return res
