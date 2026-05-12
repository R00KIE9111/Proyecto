import pymysql
import boto3

conexion = pymysql.connect(
    host='flask-db.c7saowikmas3.us-east-1.rds.amazonaws.com',
    user='admin',
    password='Inacap.2026',
    database='flask-db'
)

dynamodb = boto3.resource(
    'dynamodb',
    region_name='us-east-1'
)

tabla = dynamodb.Table('Eventos')