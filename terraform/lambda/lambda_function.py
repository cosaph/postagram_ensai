import json
from urllib.parse import unquote_plus
import boto3
import os
import logging
print('Loading function')
logger = logging.getLogger()
logger.setLevel("INFO")
s3 = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')
reckognition = boto3.client('rekognition')

table = dynamodb.Table(os.getenv("DYNAMO_TABLE"))

def lambda_handler(event, context):

    """
    This function is triggered by an object being created in an S3 bucket.
    It will detect labels in the image and update the DynamoDB table with the labels.
    """

    logger.info(json.dumps(event, indent=2))
    logger.info(f"user : {user} || task_id: {task_id}")

    bucket = event["Records"][0]["s3"]["bucket"]["name"]

    key = unquote_plus(event["Records"][0]["s3"]["object"]["key"])

    user, task_id = key.split('/')[:2]

    label_data = reckognition.detect_labels(
        Image={ "S3Object": {"Bucket": bucket,"Name": key}},
        MaxLabels=5,
        MinConfidence=0.75
    )

    logger.info(f"Labels data : {label_data}")
    logger.info(f"Labels detected : {labels}")

    labels = {label["Name"] for label in label_data["Labels"]}

    table.update_item(
        Key={"id": f"ID#{task_id}","user": f"USER#{user}"},
        UpdateExpression="SET labels = :labels",
        ExpressionAttributeValues={":labels": labels},

    )
