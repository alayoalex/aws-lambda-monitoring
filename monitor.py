import argparse
import sys
import json
import monitoring_lambda
import os
from dotenv import load_dotenv
import boto3

"""
- Agregar opcion de monitoreo a través de correo y telegram de una lambda
    > python monitor.py [nombre de la lambda]
    > python monitor.py [nombre del grupo de logs]
    > python monitor.py [nombre de la lambda] --region [region]
    > python monitor.py [nombre del grupo de logs] --region [region]
- Elminar opcion de monitoreo a través de correo y telegram de una lambda
    > python monitor.py [nombre de la lambda] --delete|-d
    > python monitor.py [nombre de la lambda] --region [region] --delete|-d
    > python monitor.py [nombre del grupo de logs] --delete|-d
    > python monitor.py [nombre del grupo de logs] --region [region] --delete|-d
* La region por defecto es us-east-2.
"""

destination_lambda = {
    'us-east-1': "function-errors-notifications-ssr-virginia",
    'us-east-2': "function-errors-notifications-ssr",
    'us-east-2-temp': "function-errors-notifications",
}

regions = ['us-east-1', 'us-east-2']

load_dotenv()

account = os.environ['aws_account']
region = os.environ['aws_region']
aws_access_key_id = os.environ['aws_access_key_id']
aws_secret_access_key = os.environ['aws_secret_access_key']


def parse_cli():
    try:
        parser = argparse.ArgumentParser()
        parser.add_argument(
            'lambda_function_or_log_group',
            type=str,
            nargs='?',
            help='Nombre de la lambda o del log group a monitorear través de telegram.')
        parser.add_argument(
            '-l', '--islambda',
            action='store_true',
            help='Si se va a pasar el nombre de una lambda se debe especificar con este comando.')
        parser.add_argument(
            "--region",
            nargs="?",
            help="AWS Region where the lambda or the log group is.",
        )
        parser.add_argument(
            "--pattern",
            nargs="*",
            help="Logs messages patterns, for example: ?ERROR, ?5xx, ?INFO, ?DEBUG, etc.",
        )
        parser.add_argument(
            '-d', '--delete',
            action='store_true',
            help='Dejar de monitorear lambda o el log group.')
        args = parser.parse_args()
        return args
    except argparse.ArgumentError as err:
        print(str(err))
        sys.exit(2)


if __name__ == "__main__":
    args = parse_cli()
    print(args)

    if str(args.region) in regions:
        session = boto3.Session(aws_access_key_id=aws_access_key_id,
                                aws_secret_access_key=aws_secret_access_key,
                                region_name=args.region)
    else:
        session = boto3.Session(aws_access_key_id=aws_access_key_id,
                                aws_secret_access_key=aws_secret_access_key,
                                region_name=region)
    lambda_client = session.client('lambda')
    logs_client = session.client('logs')

    if not args.delete:
        if args.islambda:
            print(
                f"Adding lambda function {args.lambda_function_or_log_group} to monitorization.")
            print()
            print(json.dumps(monitoring_lambda.add_lambda_for_monitoring(
                lambda_client,
                logs_client,
                destination_lambda[region],
                args.lambda_function_or_log_group,
                args.pattern,
                region, account), indent=4))
        else:
            print(
                f"Adding logs group {args.lambda_function_or_log_group} to monitorization.")
            print()
            print(json.dumps(monitoring_lambda.add_log_group_for_monitoring(
                lambda_client,
                logs_client,
                destination_lambda[region],
                args.lambda_function_or_log_group,
                args.pattern,
                region, account), indent=4))
    elif args.delete:
        if args.islambda:
            print(
                f"Deleting lambda function {args.lambda_function_or_log_group} from monitorization.")
            print()
            print(json.dumps(monitoring_lambda.remove_lambda_of_monitoring(
                lambda_client,
                logs_client,
                destination_lambda[region],
                args.lambda_function_or_log_group), indent=4))
        else:
            print(
                f"Deleting logs group {args.lambda_function_or_log_group} from monitorization.")
            print()
            print(json.dumps(monitoring_lambda.remove_log_group_of_monitoring(
                lambda_client,
                logs_client,
                destination_lambda[region],
                args.lambda_function_or_log_group), indent=4))
