# backend/config.py

import os
from dotenv import load_dotenv

load_dotenv()  # Loads .env file

class Settings:
    # AWS Credentials
    AWS_ACCESS_KEY_ID: str = os.getenv("AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY: str = os.getenv("AWS_SECRET_ACCESS_KEY")
    AWS_REGION: str = os.getenv("AWS_REGION", "us-east-1")

    # DynamoDB Tables
    DYNAMODB_PATIENTS_TABLE: str = os.getenv("DYNAMODB_PATIENTS_TABLE", "mediconnect-patients")
    DYNAMODB_CASES_TABLE: str = os.getenv("DYNAMODB_CASES_TABLE", "mediconnect-cases")
    DYNAMODB_DOCTORS_TABLE: str = os.getenv("DYNAMODB_DOCTORS_TABLE", "mediconnect-doctors")

    # WebSocket
    WEBSOCKET_URL: str = os.getenv("WEBSOCKET_URL")

    # Bedrock
    BEDROCK_MODEL_ID: str = os.getenv("BEDROCK_MODEL_ID", "meta.llama3-8b-instruct-v1:0")

    # Feature Flags
    MOCK_WHATSAPP: bool = os.getenv("MOCK_WHATSAPP", "true").lower() == "true"
    MOCK_TRANSCRIBE: bool = os.getenv("MOCK_TRANSCRIBE", "true").lower() == "true"


settings = Settings()