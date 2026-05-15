import pymysql
import boto3
from datetime import datetime

# Conexión RDS MySQL
def get_connection():
    return pymysql.connect(
        host="database-1.c7saowikmas3.us-east-1.rds.amazonaws.com",
        user="admin",
        password="Inacap.2026",
        database="gestorecommerce"
    )

# Conexión DynamoDB
dynamodb = boto3.resource("dynamodb")
tabla_evento = dynamodb.Table("Evento")

def registrar_evento(userId, accion, ip):
    tabla_evento.put_item(
        Item={
            "userId": str(userId),
            "timestamp": str(datetime.now()),
            "accion": accion,
            "ip": ip
        }
    )
