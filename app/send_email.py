import json
import logging

import boto3

from .env import AWS_REGION, AWS_ACC_ID, AWS_SECRET, CHARSET, SENDER

logger = logging.getLogger(__name__)


class MockBoto3Client:
    def send_email(self, **kwargs):
        logger.info(
            "Mail would have been sent: %s",
            json.dumps(kwargs, indent=4, sort_keys=True, ensure_ascii=False),
        )


# AWS SES
if AWS_REGION == "MOCK":
    client = MockBoto3Client()
else:
    client = boto3.client(
        "ses",
        region_name=AWS_REGION,
        aws_access_key_id=AWS_ACC_ID,
        aws_secret_access_key=AWS_SECRET,
    )


def send_email(subject, body, recipient):
    try:
        client.send_email(
            Destination={"ToAddresses": [recipient]},
            Message={
                "Subject": {"Charset": CHARSET, "Data": subject},
                "Body": {"Html": {"Charset": CHARSET, "Data": body}},
            },
            Source=SENDER,
        )
    except Exception as err:
        logger.error("Error sending email: %s", err)
