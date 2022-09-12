"""Lambda handler module."""

import json
import logging
import sys

import pymysql
from utils import get_secret

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event, context):
    """This function creates iam authentication db user on the RDS cluster."""
    request_type = event["RequestType"]

    if request_type in ["Create", "Update"]:
        props = event["ResourceProperties"]
        rds_secret = json.loads(get_secret(secret_name=props["DBSecretArn"]))
        iam_db_user = props["IAMDBUser"]

        rds_host = rds_secret["host"]
        name = rds_secret["username"]
        password = rds_secret["password"]
        db_name = rds_secret["dbname"]

        try:
            conn = pymysql.connect(
                host=rds_host, user=name, passwd=password, db=db_name, connect_timeout=5
            )
        except pymysql.MySQLError as e:
            logger.error(
                "ERROR: Unexpected error: Could not connect to MySQL instance."
            )
            logger.error(e)
            sys.exit()

        logger.info("SUCCESS: Connection to RDS MySQL instance succeeded")
        with conn.cursor() as cur:
            cur.execute(
                f"CREATE USER IF NOT EXISTS {iam_db_user} IDENTIFIED WITH AWSAuthenticationPlugin AS 'RDS';"
            )
            cur.execute(f"GRANT ALL ON `%`.* TO {iam_db_user}@`%`;")
            conn.commit()
        conn.commit()
        return {"PhysicalResourceId": f"CustomIAMDBUser{iam_db_user}"}
    elif request_type in ["Delete"]:
        return {"PhysicalResourceId": event["PhysicalResourceId"]}
