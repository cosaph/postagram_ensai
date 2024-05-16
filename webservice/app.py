import boto3
import os
from dotenv import load_dotenv
from typing import Union
import logging
from fastapi import FastAPI, Request, status, Header
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
import uuid

from getSignedUrl import getSignedUrl

app = FastAPI()
logger = logging.getLogger("uvicorn")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    exc_str = f'{exc}'.replace('\n', ' ').replace('   ', ' ')
    logger.error(f"{request}: {exc_str}")
    content = {'status_code': 10422, 'message': exc_str, 'data': None}
    return JSONResponse(content=content, status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)


class Post(BaseModel):
    title: str
    body: str


dynamodb = boto3.resource('dynamodb', region_name="us-east-1")
table = dynamodb.Table(os.getenv("DYNAMO_TABLE"))

bucket = os.getenv("BUCKET")
s3_client = boto3.client('s3', region_name="us-east-1")

@app.post("/posts")
async def post_a_post(post: Post, authorization: str | None = Header(default=None)):
    """
    Cette fonction permet de poster un article
    """
    logger.info(f"title : {post.title}")
    logger.info(f"body : {post.body}")
    logger.info(f"user : {authorization}")

    post_id = uuid.uuid4()

    post_json = {"id": f"ID#{post_id}",
                 "title": f"{post.title}",
                 "user": f"USER#{authorization}",
                 "body": f"{post.body}",}

    items = table.put_item(Item=post_json)

    return items


from typing import Union
import boto3

app = FastAPI()
table = boto3.resource('dynamodb').Table('posts')
s3_client = boto3.client('s3')
bucket = 'your-s3-bucket-name'

@app.get("/posts")
async def get_all_posts(user: Union[str, None] = None):
    """
    Cette fonction permet de récupérer tous les posts
    """
    if user is None:
        posts = table.scan()["Items"]
    else:
        posts = table.query(
            Select='ALL_ATTRIBUTES',
            ExpressionAttributeNames={"#user": "user"},
            KeyConditionExpression="#user = :user",
            ExpressionAttributeValues={
                ":user": f"USER#{user}",
            },
        )["Items"]

    for post in posts:
        if 'image' in post:
            image_name = post['image']
            presigned_url = s3_client.generate_presigned_url(
                ClientMethod='get_object',
                Params={
                    'Bucket': bucket,
                    'Key': image_name
                },
            )
            post['image_url'] = presigned_url

    return posts


@app.get("/signedUrlPut")
async def get_signed_url_put(filename: str,filetype: str, postId: str,authorization: str | None = Header(default=None)):
    return getSignedUrl(filename, filetype, postId, authorization)



@app.delete("/posts/{post_id}")
async def get_post_user_id(post_id: str):
    return ()


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080, log_level="debug")
