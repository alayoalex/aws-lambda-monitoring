import json
import logging
import lambda_wrapper
import logs_wrapper


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def remove_all_lambda_permissions(logs_client, lambda_name):
    policy_statements_id_list = get_lambda_policy_statements(
        logs_client, lambda_name)
    for statement in policy_statements_id_list:
        print(lambda_wrapper.remove_lambda_permission(
            logs_client, lambda_name, statement))


def get_lambda_policy_statements(logs_client, lambda_name):
    res = json.loads(lambda_wrapper.get_lambda_policy(
        logs_client, lambda_name)['Policy'])
    statements = []
    for r in res["Statement"]:
        statements.append(r["Sid"])
    return statements


def exist_subcription_filter(logs_client, log_group_name):
    subcription_filters = logs_wrapper.list_subcription_filters(logs_client)
    for sflist in subcription_filters:
        for sf in sflist:
            if sf['logGroupName'] == log_group_name:
                return True
    return False


def add_log_group_for_monitoring(lambda_client,
                                 logs_client,
                                 destination_lambda_name,
                                 log_group_name, pattern, region, account):
    if not logs_wrapper.exist_log_group(logs_client, log_group_name):
        raise Exception(f'The {log_group_name} does not exist.')
    response_lambda = lambda_wrapper.add_lambda_permission(
        lambda_client, destination_lambda_name, log_group_name, account, region)
    response_logs = logs_wrapper.create_subcription_filter(
        logs_client, destination_lambda_name, log_group_name, pattern, region, account)
    return {'response': [response_lambda, response_logs]}


def remove_log_group_of_monitoring(lambda_client, logs_client, destination_lambda_name, log_group_name):
    res = json.loads(lambda_wrapper.get_lambda_policy(
        lambda_client, destination_lambda_name)['Policy'])
    statements = res['Statement']
    for s in statements:
        ln = s['Sid'].split('_')[1]
        if ln == log_group_name.split('/')[-1]:
            lambda_wrapper.remove_lambda_permission(
                lambda_client, destination_lambda_name, s['Sid'])
    return logs_wrapper.remove_subcription_filter(logs_client, log_group_name)


def add_lambda_for_monitoring(lambda_client,
                              logs_client,
                              destination_lambda_name,
                              lambda_name, pattern, region, account):
    log_group_name = "/aws/lambda/{}".format(lambda_name)
    if not logs_wrapper.exist_log_group(logs_client, log_group_name):
        logs_wrapper.create_lambda_log_group(logs_client, lambda_name)
    response_lambda = lambda_wrapper.add_lambda_permission(
        lambda_client, destination_lambda_name, log_group_name, account, region)
    response_logs = logs_wrapper.create_subcription_filter(
        logs_client, destination_lambda_name, log_group_name, pattern, region, account)
    return {'response': [response_lambda, response_logs]}


def remove_lambda_of_monitoring(lambda_client, logs_client, destination_lambda_name, lambda_name):
    res = json.loads(lambda_wrapper.get_lambda_policy(
        lambda_client, destination_lambda_name)['Policy'])
    statements = res['Statement']
    for s in statements:
        ln = s['Sid'].split('_')[1]
        if ln == lambda_name:
            lambda_wrapper.remove_lambda_permission(
                lambda_client, destination_lambda_name, s['Sid'])
    return logs_wrapper.remove_subcription_filter(logs_client, "/aws/lambda/{}".format(lambda_name))


if __name__ == "__main__":
    print(lambda_wrapper.invoke_lambda_function(
        lambda_client, "hello-world-lambda-py", {}))
    # print(json.dumps(logs_wrapper.list_logs_events(
    #     '/aws/lambda/ssr-themes-elroisupplies-develop-api'), indent=4))
