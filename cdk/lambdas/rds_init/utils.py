"""Utilitis module for lambda function."""

import base64
import os

import boto3
from botocore.exceptions import ClientError


def get_secret(secret_name):
    """This function gets a secret from secrets manager and returns it's value."""
    region_name = os.environ["AWS_REGION"]
    session = boto3.session.Session()
    client = session.client(service_name="secretsmanager", region_name=region_name)

    try:
        get_secret_value_response = client.get_secret_value(SecretId=secret_name)
    except ClientError as e:
        raise e
    else:
        if "SecretString" in get_secret_value_response:
            secret = get_secret_value_response["SecretString"]
            return secret
        else:
            decoded_binary_secret = base64.b64decode(
                get_secret_value_response["SecretBinary"]
            )
            return decoded_binary_secret
