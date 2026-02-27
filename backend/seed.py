# backend/seed.py

import time
from decimal import Decimal
import boto3
from botocore.exceptions import ClientError
from backend.config import settings


dynamodb = boto3.client(
    "dynamodb",
    region_name=settings.AWS_REGION,
    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
)


def create_patients_table():
    try:
        dynamodb.create_table(
            TableName=settings.DYNAMODB_PATIENTS_TABLE,
            KeySchema=[
                {"AttributeName": "PatientID", "KeyType": "HASH"}
            ],
            AttributeDefinitions=[
                {"AttributeName": "PatientID", "AttributeType": "S"},
                {"AttributeName": "ASHAWorkerID", "AttributeType": "S"},
                {"AttributeName": "Village", "AttributeType": "S"},
            ],
            GlobalSecondaryIndexes=[
                {
                    "IndexName": "ASHAWorkerID-index",
                    "KeySchema": [
                        {"AttributeName": "ASHAWorkerID", "KeyType": "HASH"}
                    ],
                    "Projection": {"ProjectionType": "ALL"},
                },
                {
                    "IndexName": "Village-index",
                    "KeySchema": [
                        {"AttributeName": "Village", "KeyType": "HASH"}
                    ],
                    "Projection": {"ProjectionType": "ALL"},
                },
            ],
            BillingMode="PAY_PER_REQUEST",
        )
        print("✅ Patients table created")
    except ClientError as e:
        if e.response["Error"]["Code"] == "ResourceInUseException":
            print("ℹ️ Patients table already exists")
        else:
            raise


def create_cases_table():
    try:
        dynamodb.create_table(
            TableName=settings.DYNAMODB_CASES_TABLE,
            KeySchema=[
                {"AttributeName": "CaseID", "KeyType": "HASH"}
            ],
            AttributeDefinitions=[
                {"AttributeName": "CaseID", "AttributeType": "S"},
                {"AttributeName": "PatientID", "AttributeType": "S"},
                {"AttributeName": "Status", "AttributeType": "S"},
            ],
            GlobalSecondaryIndexes=[
                {
                    "IndexName": "PatientID-index",
                    "KeySchema": [
                        {"AttributeName": "PatientID", "KeyType": "HASH"}
                    ],
                    "Projection": {"ProjectionType": "ALL"},
                },
                {
                    "IndexName": "Status-index",
                    "KeySchema": [
                        {"AttributeName": "Status", "KeyType": "HASH"}
                    ],
                    "Projection": {"ProjectionType": "ALL"},
                },
            ],
            BillingMode="PAY_PER_REQUEST",
        )
        print("✅ Cases table created")
    except ClientError as e:
        if e.response["Error"]["Code"] == "ResourceInUseException":
            print("ℹ️ Cases table already exists")
        else:
            raise


def create_doctors_table():
    try:
        dynamodb.create_table(
            TableName=settings.DYNAMODB_DOCTORS_TABLE,
            KeySchema=[
                {"AttributeName": "DoctorID", "KeyType": "HASH"}
            ],
            AttributeDefinitions=[
                {"AttributeName": "DoctorID", "AttributeType": "S"},
            ],
            BillingMode="PAY_PER_REQUEST",
        )
        print("✅ Doctors table created")
    except ClientError as e:
        if e.response["Error"]["Code"] == "ResourceInUseException":
            print("ℹ️ Doctors table already exists")
        else:
            raise


def seed_demo_doctors():
    table = boto3.resource(
        "dynamodb",
        region_name=settings.AWS_REGION,
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
    ).Table(settings.DYNAMODB_DOCTORS_TABLE)

    doctors = [
    {
        "DoctorID": "DR-001",
        "Name": "Dr. Priya Patel",
        "Specialization": "Gynaecologist",
        "Lat": Decimal("25.5941"),
        "Lng": Decimal("85.1376"),
        "IsAvailable": True,
    },
    {
        "DoctorID": "DR-002",
        "Name": "Dr. Ramesh Sharma",
        "Specialization": "General Physician",
        "Lat": Decimal("25.6121"),
        "Lng": Decimal("85.1534"),
        "IsAvailable": True,
    },
    {
        "DoctorID": "DR-003",
        "Name": "Dr. Anita Singh",
        "Specialization": "Paediatrician",
        "Lat": Decimal("25.5712"),
        "Lng": Decimal("85.1892"),
        "IsAvailable": True,
    },
]

    for doc in doctors:
        table.put_item(Item=doc)

    print("✅ Demo doctors seeded")


if __name__ == "__main__":
    create_patients_table()
    create_cases_table()
    create_doctors_table()

    print("⏳ Waiting 5 seconds for tables...")
    time.sleep(5)

    seed_demo_doctors()

    print("🎉 ASHA module database ready!")