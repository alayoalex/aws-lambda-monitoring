# aws-lambda-monitoring

Python script to monitoring aws lambda functions and send error messages to a Telegram Channel and get logs through a Telegram Bot.

* [x] Dado el nombre de una función lambda
1. Comprobar si existe el log group de esa lambda en CloudWatch
2. Si no se existe el log group de esa lambda en CloudWatch, entonces crearlo
3. Crear un log subscription filter para el log group de la lambda con el patrón "?5xx ?ERROR" si no existe
4. Agregar un trigger a la lambda que notifica de errores a través de email o telegram

* [x] Dado el nombre de una función lambda
1. Remover el trigger de la función lambda que notifica de errores a través de email o telegram
2. Remover el subscription filter del log group de esa lambda

* Obtener tamaño de la policy de la lambda que notifica de errores a través de email o telegram
* [x] Obtener todos los triggers que tiene la lambda


#-------------------

usage: monitor.py [-h] [-l] [--region [REGION]] [--pattern [PATTERN]] [-d] [lambda_function_or_log_group]

positional arguments:
  lambda_function_or_log_group
                        Nombre de la lambda o del log group a monitorear través de telegram.

optional arguments:
  -h, --help            show this help message and exit
  -l, --islambda        Si se va a pasar el nombre de una lambda se debe especificar con este comando.
  --region [REGION]     AWS Region where the lambda or the log group is.
  --pattern [PATTERN]   Logs messages patterns, for example: ?ERROR, ?5xx, ?INFO, ?DEBUG, etc.
  -d, --delete          Dejar de monitorear lambda o el log group.

python monitor.py -h
python monitor.py [nombre de la lambda] -l
python monitor.py [nombre del log group completo]        # por ejemplo: /aws/lambda/lambda-scrapping
python monitor.py [nombre de la lambda] -l --region us-east-1
python monitor.py [nombre de la lambda] -l --pattern ?ERROR ?5xx ?DEBUG
python monitor.py [nombre del log group completo]        # por ejemplo: /aws/lambda/lambda-scrapping
python monitor.py [nombre de la lambda] -l --region us-east-1 --pattern ?INFO
python monitor.py [nombre de la lambda] -d -l
python monitor.py [nombre de la region completo] -d
python monitor.py [nombre de la lambda] -d -l --region us-east-1
python monitor.py [nombre del log group completo] -d --region us-east-1

us-east-2 es la region por defecto si no se incluye este argumento en las opciones
el pattern por defecto de envio de mensajes a telegram es '?ERROR ?5xx', es decir, mensajes de errores. Estos parametros van separados por espacios