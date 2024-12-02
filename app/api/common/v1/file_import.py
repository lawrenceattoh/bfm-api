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
    ADMINISTRATION_RIGHTS = 'administration_rights'
    # MECHANICAL_RIGHTS = 'mechanical_rights'
    # SYNC_RIGHTS = 'sync_rights'


class RecordingRightsType(Enum):
    RECORDING_OWNERSHIP = 'recording_ownership'
    DISTRIBUTION_RIGHTS = 'distribution_rights'
    # PERFORMANCE_RIGHTS = 'performance_rights'
    # MERCHANDISING_RIGHTS = 'merchandising_rights'
    NEIGHBORING_RIGHTS = 'neighboring_rights'


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
                    deal_name: str = Form(),
                    completed_date: datetime.date = Form(),
                    right_type: PublishingRightsType = Form(),
                    is_controlled: bool = Form(),
                    territories: List[str] | None = Form(None),
                    mech_share: float = Form(None),
                    reversion_date: datetime.date = Form(None),
                    rms_user=Depends(get_user)):
    main_copyright_type = 'publishing'
    file_content = await file.read()
    file_content_string = file_content.decode('utf-8-sig')
    data = read_csv_file(file_content_string,
                         deal_name=deal_name,
                         completed_date=completed_date,
                         main_copyright=main_copyright_type,
                         right_type=right_type.value,
                         territories=territories,
                         mech_share=mech_share,
                         is_controlled=is_controlled,
                         reversion_date=reversion_date
                         )
    res = run_import(main_copyright_type, data, rms_user)
    return 1


@router.post('/schedule/recordings')
async def load_file(file: UploadFile = File(), deal_name: str = Form(), completed_date: datetime.date = Form(),
                    rights_type: RecordingRightsType = Form(),
                    business_entity: str = Form(),
                    rms_user=Depends(get_user)):
    main_copyright_type = 'recording'
    file_content = await file.read()
    file_content_string = file_content.decode('utf-8-sig')

    data = read_csv_file(file_content_string, deal_name=deal_name, completed_date=completed_date,
                         copyright=copyright, rights_type=rights_type, business_entity=business_entity)
    res = run_import(main_copyright_type, data, rms_user)
    return 1
