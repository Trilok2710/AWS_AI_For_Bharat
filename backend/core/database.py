# backend/core/database.py

import uuid
from typing import Optional, Dict, Any, List

import boto3
from boto3.dynamodb.conditions import Key, Attr
from botocore.exceptions import ClientError

from backend.config import settings


# Initialize DynamoDB resource (single instance)
dynamodb = boto3.resource(
    "dynamodb",
    region_name=settings.AWS_REGION,
    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
)

patients_table = dynamodb.Table(settings.DYNAMODB_PATIENTS_TABLE)
cases_table = dynamodb.Table(settings.DYNAMODB_CASES_TABLE)
doctors_table = dynamodb.Table(settings.DYNAMODB_DOCTORS_TABLE)


# -----------------------------
# Utility Functions
# -----------------------------

def generate_uuid(prefix: str) -> str:
    """Generate prefixed UUID (e.g., PAT-xxxx, CASE-xxxx)"""
    return f"{prefix}-{str(uuid.uuid4())[:8]}"


# -----------------------------
# Generic CRUD Helpers
# -----------------------------

def put_item(table, item: Dict[str, Any]) -> Dict[str, Any]:
    try:
        table.put_item(Item=item)
        return item
    except ClientError as e:
        raise Exception(f"DynamoDB Put Error: {e.response['Error']['Message']}")


def get_item(table, key: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    try:
        response = table.get_item(Key=key)
        return response.get("Item")
    except ClientError as e:
        raise Exception(f"DynamoDB Get Error: {e.response['Error']['Message']}")


def update_item(
    table,
    key: Dict[str, Any],
    update_expression: str,
    expression_values: Dict[str, Any],
    expression_names: Optional[Dict[str, str]] = None,
) -> Dict[str, Any]:
    try:
        response = table.update_item(
            Key=key,
            UpdateExpression=update_expression,
            ExpressionAttributeValues=expression_values,
            ExpressionAttributeNames=expression_names or {},
            ReturnValues="ALL_NEW",
        )
        return response.get("Attributes", {})
    except ClientError as e:
        raise Exception(f"DynamoDB Update Error: {e.response['Error']['Message']}")


def query_items(
    table,
    key_condition,
    index_name: Optional[str] = None,
    filter_expression=None,
) -> List[Dict[str, Any]]:
    try:
        params = {
            "KeyConditionExpression": key_condition,
        }
        if index_name:
            params["IndexName"] = index_name
        if filter_expression:
            params["FilterExpression"] = filter_expression

        response = table.query(**params)
        return response.get("Items", [])
    except ClientError as e:
        raise Exception(f"DynamoDB Query Error: {e.response['Error']['Message']}")


def scan_items(
    table,
    filter_expression=None
) -> List[Dict[str, Any]]:
    try:
        params = {}
        if filter_expression:
            params["FilterExpression"] = filter_expression

        response = table.scan(**params)
        return response.get("Items", [])
    except ClientError as e:
        raise Exception(f"DynamoDB Scan Error: {e.response['Error']['Message']}")