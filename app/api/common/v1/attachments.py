import datetime
import json
import logging
import os
from typing import List

import requests
from fastapi import APIRouter, File, UploadFile, HTTPException, Form, Depends, Query
from google.cloud import storage
from google.oauth2 import service_account
from neomodel import db
from pydantic import BaseModel, field_validator

from app.api.utils import get_user
from app.models import _base
from app.models.query_managers.misc.attachments import merge_attachments, get_attachments_cypher
from app.schemas.utils import convert_datetime

router = APIRouter(prefix="/v1/attachments", tags=["attachments"])

BUCKET_NAME = "bfm-digital-master-store"

logger = logging.getLogger(__name__)

if os.environ.get('ENVIRONMENT', 'dev') == 'prod':
    sa = json.loads(os.environ.get('service_account'))
    creds = service_account.Credentials.from_service_account_info(sa)


def create_client():
    if os.environ.get('ENVIRONMENT', 'dev') == 'prod':
        return storage.Client(credentials=creds)
    return storage.Client()


def set_expiry():
    return datetime.datetime.now() + datetime.timedelta(minutes=5)


async def merge_with_db(entity_id: str, attachment_type: str, attachment_category: str, filename: str, blob_url: str,
                        rms_user: str):
    try:
        params = {
            "entity_id": entity_id,
            "attachment_type": attachment_type,
            "attachment_category": attachment_category,
            "filename": filename,
            "blob_url": blob_url,
            "rms_user": rms_user,
        }
        db.cypher_query(merge_attachments(), params)
        logger.info(f"Successfully merged {filename} into the database.")
    except Exception as e:
        logger.error(f"Failed to merge {filename} into the database: {e}")
        raise HTTPException(status_code=500, detail="Database merge failed")


async def upload_to_gcs(node_label, entity_id, attachment_type, attachment_category, file: UploadFile, filename: str,
                        client):
    try:
        print(client)
        print(type(client))
        bucket = client.bucket(BUCKET_NAME)
        storage_path = f"{node_label}/{entity_id}/{attachment_category}/{attachment_type}/{filename}"
        blob = bucket.blob(storage_path)

        signed_url = blob.generate_signed_url(
            expiration=set_expiry(),
            method="PUT",
            version="v4",
            credentials=creds if os.environ.get('environment', 'dev') == 'prod' else None,
        )
        res = requests.put(signed_url, data=file.file)
        if res.status_code != 200:
            raise Exception(f"Upload failed for {filename}: {res.content}")

        logger.info(f"Uploaded {filename} to {storage_path}")
        return storage_path
    except Exception as e:
        logger.error(f"Failed to upload {filename}: {e}")
        raise HTTPException(status_code=500, detail=f"Upload failed for {filename}")


@router.post("/upload")
async def upload_attachments(
        entity_id: str = Form(...),
        node_label: str = Form(...),
        categories: List[str] = Form(...),
        types: List[str] = Form(...),
        filenames: List[str] = Form(...),
        files: List[UploadFile] = File(...),
        rms_user: str = Depends(get_user),
        client=Depends(create_client)
):
    if len(files) != len(filenames) or len(files) != len(categories) or len(files) != len(types):
        raise HTTPException(
            status_code=400, detail="The number of files, filenames, categories, and types must match."
        )
    print(rms_user)
    for file, filename, attachment_category, attachment_type in zip(files, filenames, categories, types):
        try:
            blob_url = await upload_to_gcs(
                entity_id=entity_id,
                node_label=node_label,
                attachment_type=attachment_type,
                attachment_category=attachment_category,
                file=file,
                filename=filename,
                client=client
            )

            await merge_with_db(
                entity_id=entity_id,
                attachment_type=attachment_type,
                attachment_category=attachment_category,
                filename=filename,
                blob_url=blob_url,
                rms_user=rms_user,
            )

        except Exception as e:
            logger.error(f"Error processing file {filename}: {e}")
            raise HTTPException(status_code=500, detail=f"Error processing file {filename}")

    return {"message": "Files uploaded successfully and merged with the database."}


class Attachment(BaseModel):
    filename: str
    blob_url: str
    attachment_category: str
    attachment_type: str
    created_by: str
    created_at: datetime.datetime
    uploaded_by: str
    uploaded_at: datetime.datetime

    @field_validator('created_at', 'uploaded_at', mode='before')
    @classmethod
    def validate_date_fields(cls, value):
        return convert_datetime(value)


class Attachments(BaseModel):
    attachments: List[Attachment]


@router.get("/", response_model=Attachments)
async def get_attachments(entity_id: str = Query(alias='entityId')):
    res, schema = db.cypher_query(get_attachments_cypher(), {"entity_id": entity_id})
    return {'attachments': _base.parse_neo_response(res, schema, is_many=True)}
