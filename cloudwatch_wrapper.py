import botocore
import boto3
import json
import logging
import os
from dotenv import load_dotenv

load_dotenv()

account = os.environ['aws_account']
region = os.environ['aws_region']
aws_access_key_id = os.environ['aws_access_key_id']
aws_secret_access_key = os.environ['aws_secret_access_key']

session = boto3.Session(aws_access_key_id=aws_access_key_id,
                        aws_secret_access_key=aws_secret_access_key,
                        region_name=region)
cloudwatch_client = session.client('cloudwatch')

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
