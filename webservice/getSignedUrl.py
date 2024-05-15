import logging
import boto3
import os
import uuid
from pathlib import Path
from botocore.exceptions import ClientError


bucket = os.getenv("BUCKET")
s3_client = boto3.client(
    's3',
    config=boto3.session.Config(signature_version='s3v4'),
    region_name="us-east-1"
    )
logger = logging.getLogger("uvicorn")
print(bucket)


def getSignedUrl(filename: str, filetype: str, postId: str, user):

    filename = f'{uuid.uuid4()}{Path(filename).name}'
    object_name = f"{user}/{postId}/{filename}"

    try:
        url = s3_client.generate_presigned_url(
            Params={
                "Bucket": bucket,
                "Key": object_name,
                "ContentType": filetype
            },
            ClientMethod='put_object'
        )
    except ClientError as e:
        logging.error(e)

    logger.info(f'Url: {url}')
    return {
            "uploadURL": url,
            "objectName": object_name
        }
