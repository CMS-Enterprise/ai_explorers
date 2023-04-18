import json
import boto3
import os
import uuid
from decimal import Decimal

class DecimalEncoder(json.JSONEncoder):
  def default(self, obj):
    if isinstance(obj, Decimal):
      return float(obj)
    return json.JSONEncoder.default(self, obj)

if os.environ.get('AWS_SAM_LOCAL'):
    url = 'http://host.docker.internal:8000'
else:
    url = None

dynamodb = boto3.resource('dynamodb', endpoint_url=url)
table = dynamodb.Table(os.environ['SYSTEM_TABLE'])

def create_system(event, context):
    body = json.loads(event['body'])
    sysid = uuid.uuid4().hex
    print(body)
    item = {'sysid': sysid, 'name': body['name']}
    resp = table.put_item(Item=item)
    print(resp)
    return {
        'statusCode': 200,
        'body': json.dumps(item, cls=DecimalEncoder)
    }

def get_system(event, context):
    resp = table.get_item(Key={'sysid': event['pathParameters']['sysid']})
    item = resp.get('Item')
    if item is not None:
        return {
            'statusCode': 200,
            'body': json.dumps(item, cls=DecimalEncoder)
        }
    else:
        return {
            'statusCode': 404
        }

def list_systems(event, context):
    resp = table.scan()
    return {
        'statusCode': 200,
        'body': json.dumps(resp['Items'], cls=DecimalEncoder)
    }

def delete_system(event, context):
    resp = table.delete_item(Key={'sysid': event['pathParameters']['sysid']})
    return {
        'statusCode': 202,
    }