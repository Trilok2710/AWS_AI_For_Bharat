import boto3
from botocore.exceptions import ClientError, NoCredentialsError
from config import settings

REGION = "ap-south-1"  # change if needed
sts = boto3.client(
    "sts",
    region_name=settings.AWS_REGION,
    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
)
def test_sts():
    print("\n🔍 Testing STS (Identity)...")
    try:
        sts = boto3.client("sts", region_name=REGION)
        identity = sts.get_caller_identity()
        print("✅ STS OK")
        print("Account:", identity["Account"])
        print("ARN:", identity["Arn"])
    except Exception as e:
        print("❌ STS Failed:", e)


def test_dynamodb():
    print("\n🔍 Testing DynamoDB...")
    try:
        dynamodb = boto3.client("dynamodb", region_name=REGION)
        tables = dynamodb.list_tables()
        print("✅ DynamoDB OK")
        print("Tables:", tables.get("TableNames", []))
    except ClientError as e:
        print("❌ DynamoDB Access Denied")
        print("Error:", e.response["Error"]["Message"])
    except Exception as e:
        print("❌ DynamoDB Failed:", e)


def test_bedrock():
    print("\n🔍 Testing Bedrock...")
    try:
        bedrock = boto3.client("bedrock", region_name=REGION)
        models = bedrock.list_foundation_models()
        print("✅ Bedrock OK")
        print("Available models count:", len(models.get("modelSummaries", [])))
    except ClientError as e:
        print("❌ Bedrock Access Denied")
        print("Error:", e.response["Error"]["Message"])
    except Exception as e:
        print("❌ Bedrock Failed:", e)


def test_s3():
    print("\n🔍 Testing S3...")
    try:
        s3 = boto3.client("s3", region_name=REGION)
        buckets = s3.list_buckets()
        print("✅ S3 OK")
        print("Buckets:", [b["Name"] for b in buckets.get("Buckets", [])])
    except ClientError as e:
        print("❌ S3 Access Denied")
        print("Error:", e.response["Error"]["Message"])
    except Exception as e:
        print("❌ S3 Failed:", e)


if __name__ == "__main__":
    print("🚀 AWS Access Diagnostic")
    test_sts()
    test_dynamodb()
    test_bedrock()
    test_s3()
    print("\nDone.")