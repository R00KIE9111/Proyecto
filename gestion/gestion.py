import boto3
import datetime
import uuid

# Cliente DynamoDB
dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
tabla = dynamodb.Table('Evento')

def registrar_evento(userId, accion, ip):
    evento = {
        'eventoId': str(uuid.uuid4()),
        'userId': userId,
        'accion': accion,
        'ip': ip,
        'fecha': datetime.datetime.utcnow().isoformat()
    }
    tabla.put_item(Item=evento)
    return True
