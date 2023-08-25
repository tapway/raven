import boto3
from botocore.exceptions import ClientError
import json
from typing import Dict
import yaml
from pathlib import Path

def get_channels_from_yaml(path: str) -> Dict:
        """
        `path`: absolute path of an yaml file containing channel names and ids
        """
        p = Path(path)
        with p.open("r") as f:
            config = yaml.safe_load(f)
            return config["channels"]

def load_secret_from_aws_sm(secret_name="alertbot/slack"):
    secret_name = secret_name
    region_name = "ap-southeast-1"
    # Create a Secrets Manager client
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name
    )

    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name
        )
    except ClientError as e:
        # For a list of exceptions thrown, see
        # https://docs.aws.amazon.com/secretsmanager/latest/apireference/API_GetSecretValue.html
        raise e

    # Decrypts secret using the associated KMS key.
    secret = json.loads(get_secret_value_response['SecretString'])
    return secret["BOT_TOKEN"]
