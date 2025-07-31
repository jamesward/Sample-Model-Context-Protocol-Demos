from crhelper import CfnResource
import logging
import boto3

logger = logging.getLogger(__name__)

helper = CfnResource(json_logging=False, log_level='DEBUG', boto_level='CRITICAL', sleep_on_delete=120, ssl_verify=None)

@helper.create
def create(event, context):
    logger.info(f"Received event: {event}")
    logger.info(f"Received event: {context}")

@helper.update
def update(event, context):
    logger.info(f"Received event: {event}")
    logger.info(f"Received event: {context}")

@helper.delete
def delete(event, context):
    logger.info(f"Received event: {event}")
    logger.info(f"Received event: {context}")

def handler(event, context):
    helper(event, context)
