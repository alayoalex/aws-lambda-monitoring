import botocore
import boto3
import logging
import os
from dotenv import load_dotenv
import uuid


load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def _random_string(string_length=10):
    """Returns a random string of length string_length."""
    random = str(uuid.uuid4())  # Convert UUID format to a Python string.
    random = random.upper()  # Make all characters uppercase.
    random = random.replace("-", "")  # Remove the UUID '-'.
    return random[0:string_length]  # Return the random string.


def get_logs_groups(logs_client):
    try:
        logger.info("Retrieving logs groups list.")
        paginator = logs_client.get_paginator('describe_log_groups')
        logs_list = []
        for response in paginator.paginate(PaginationConfig={
            'MaxItems': 300,
            'PageSize': 5
        }):
            for log in response.get('logGroups', []):
                logs_list.append(log)
        logger.info("Logs groups retrieved successfully.")
        return logs_list
    except botocore.exceptions.ClientError as error:
        raise error


def exist_log_group(logs_client, log_group_name):
    try:
        logger.info("Checking if log group %s exists.", log_group_name)
        paginator = logs_client.get_paginator('describe_log_groups')
        for response in paginator.paginate(PaginationConfig={
            'MaxItems': 300,
            'PageSize': 5
        }):
            for log in response.get('logGroups', []):
                if log['logGroupName'] == log_group_name:
                    return True
        logger.info("The log group %s doesn't exist.", log_group_name)
        return False
    except botocore.exceptions.ClientError as error:
        raise error


def create_lambda_log_group(logs_client, lambda_name):
    try:
        logger.info("Creating log group for lambda: %s.", lambda_name)
        response = logs_client.create_log_group(
            logGroupName='/aws/lambda/{}'.format(lambda_name),
        )
        logger.info("Created log group.")
        return response
    except botocore.exceptions.ClientError as error:
        raise error


def list_subcription_filters(logs_client):
    try:
        logger.info("Retrieving subscription filters from all logs groups.")
        list_log_groups = get_logs_groups(logs_client)
        subscription_filters = []
        for log_group in list_log_groups:
            log_group_name = log_group["logGroupName"]
            response = logs_client.describe_subscription_filters(
                logGroupName=log_group_name)
            if len(response["subscriptionFilters"]) != 0:
                subscription_filters.append(response["subscriptionFilters"])
        logger.info("Subscription filters retrieved successfully.")
        return subscription_filters
    except botocore.exceptions.ClientError as error:
        raise error


def create_subcription_filter(logs_client, destination_lambda_function, log_group_name, pattern, region, account):
    try:
        logger.info(
            "Creating subscription filter for logs group name: %s.", log_group_name)

        if pattern != None:
            filter_pattern = ' '.join(pattern) if len(pattern) > 1 else pattern
        else:
            filter_pattern = '?ERROR ?5xx'

        response = logs_client.put_subscription_filter(
            destinationArn='arn:aws:lambda:{}:{}:function:{}'.format(
                region, account, destination_lambda_function),
            filterName='{}_{}'.format(log_group_name.split(
                '/')[-1], _random_string(string_length=10)),
            filterPattern=filter_pattern,
            logGroupName=log_group_name,
        )

        logger.info("Subscription filter created successfully.")
        return response

    except botocore.exceptions.ClientError as error:
        raise error


def remove_subcription_filter(logs_client, log_group_name):
    try:
        logger.info(
            "Removing subscription filter for logs group name: %s.", log_group_name)
        response = logs_client.delete_subscription_filter(
            logGroupName=log_group_name,
            filterName=log_group_name.split('/')[-1]
        )
        logger.info("Subscription filter removed successfully.")
        return response
    except botocore.exceptions.ClientError as error:
        raise error


def list_log_streams(logs_client, log_group_name):
    try:
        response = logs_client.describe_log_streams(
            logGroupName=log_group_name,
            orderBy='LastEventTime',
            descending=True,
            limit=10
        )
        return response
    except botocore.exceptions.ClientError as error:
        raise error


def list_logs_events(logs_client, log_group_name):
    logs_streams = list_log_streams(logs_client, log_group_name)['logStreams']
    try:
        response = logs_client.get_log_events(
            logGroupName=log_group_name,
            logStreamName=logs_streams[0]['logStreamName'],
            startFromHead=False
        )
        return response
    except botocore.exceptions.ClientError as error:
        raise error
