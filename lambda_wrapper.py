import botocore
import boto3
import json
import logging
import uuid


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def _random_string(string_length=10):
    """Returns a random string of length string_length."""
    random = str(uuid.uuid4())  # Convert UUID format to a Python string.
    random = random.upper()  # Make all characters uppercase.
    random = random.replace("-", "")  # Remove the UUID '-'.
    return random[0:string_length]  # Return the random string.


def add_lambda_permission(lambda_client, destination_lambda_name, log_group_name, account, region):
    try:
        logger.info("Adding permission to %s log group to send errors logs to function %s.",
                    log_group_name, destination_lambda_name)
        response = lambda_client.add_permission(
            FunctionName=destination_lambda_name,
            StatementId="lambda_{}_{}".format(
                log_group_name.split('/')[-1], _random_string(6)),
            Action='lambda:InvokeFunction',
            Principal='logs.{}.amazonaws.com'.format(region),
            SourceArn='arn:aws:logs:{}:{}:log-group:{}:*'.format(
                region,
                account,
                log_group_name),
            SourceAccount=account
        )
        logger.info("Permission added succesfully")
        return response
    except botocore.exceptions.ClientError as error:
        raise error


def remove_lambda_permission(lambda_client, destination_lambda_name, statement_id):
    try:
        logger.info("Removing statement %s from lambda %s policy.",
                    statement_id, destination_lambda_name)
        response = lambda_client.remove_permission(
            FunctionName=destination_lambda_name,
            StatementId=statement_id,
        )
        logger.info("Permission removed succesfully")
        return response
    except botocore.exceptions.ClientError as error:
        raise error


def get_lambda_policy(lambda_client, lambda_name):
    try:
        logger.info("Getting permission policy of lambda: %s", lambda_name)
        response = lambda_client.get_policy(
            FunctionName=lambda_name
        )
        logger.info("Policy retrieved succesfully")
        return response
    except botocore.exceptions.ClientError as error:
        raise error


def invoke_lambda_function(lambda_client, function_name, function_params):
    """
    Invokes an AWS Lambda function.

    :param function_name: The name of the function to invoke.
    :param function_params: The parameters of the function as a dict. This dict
                            is serialized to JSON before it is sent to AWS Lambda.
    :return: The response from the function invocation.
    """
    try:
        response = lambda_client.invoke(
            FunctionName=function_name,
            Payload=json.dumps(function_params).encode())
        logger.info("Invoked function %s.", function_name)
        return response
    except botocore.exceptions.ClientError as error:
        raise error


def list_lambda_functions(lambda_client):
    try:
        paginator = lambda_client.get_paginator('list_functions')
        lambda_list = []
        for response in paginator.paginate(PaginationConfig={
            'MaxItems': 300,
            'PageSize': 20
        }):
            for l in response.get('Functions', []):
                lambda_list.append(l)
        return lambda_list
    except botocore.exceptions.ClientError as error:
        raise error
