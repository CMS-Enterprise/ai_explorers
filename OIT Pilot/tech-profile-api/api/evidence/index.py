from datetime import datetime
from decimal import Decimal
import io
import json
import os
from urllib.parse import urlparse

import boto3
import docx
import requests
import spacy
import pandas

from entity_linker import EntityLinker

nlp = spacy.load('en_core_web_trf')
linker = nlp.add_pipe('entity-linker', config={'data_dir': '/opt/ml/model/', 'use_entities': True})

if os.environ.get('AWS_SAM_LOCAL'):
    url = 'http://host.docker.internal:8000'
else:
    url = None

def get_text_from_docx(f):
    doc = docx.Document(f)
    fullText = []
    for para in doc.paragraphs:
        fullText.append(para.text)
    return '\n'.join(fullText).strip()

def get_text_evidence(doc):
    parsed_url = urlparse(doc['url'])
    if parsed_url.scheme == 's3':
        with io.BytesIO() as f:
            s3.download_fileobj(parsed_url.netloc, parsed_url.path, f)
            if doc['contentType'] == 'application/msword':
                text = get_text_from_docx(f)
            elif doc['contentType'] == 'text/plain':
                text = f.read()
    elif parsed_url.scheme.startswith('http'):
        resp = requests.get(doc['url'])
        if doc['contentType'] == 'application/msword':
            with io.BytesIO(resp.content) as f:
                text = get_text_from_docx(f)
        elif doc['contentType'] == 'text/plain':
            text = resp.content.decode('ascii')
    return text.strip()

def get_entity_types(cui):
    match = linker.kb.cui_to_entity.get(cui)
    if match is not None:
        return match.types
    else:
        return []

dynamodb = boto3.resource('dynamodb', endpoint_url=url)
s3 = boto3.resource('s3')
table = dynamodb.Table(os.environ['SYSTEM_TABLE'])

with open('/opt/ml/model/wd_pip_packages.json') as f:
    pip_packages = json.load(f)

with open('/opt/ml/model/wd_npm_packages.json') as f:
    npm_packages = json.load(f)

def handler(event, context):
    """
    Handle /evidence API endpoint
    Acceptable Bodies
    {
        'name': 'SBOM from Splunk',
        'type': 'sbom',
        'evidence': {sbom body}
    }
    {
        'name': 'GitHub README',
        'type': 'document',
        'evidence': {
            'url': '',
            'contentType': ''
        }
    }
    """
    now = datetime.now().isoformat()
    sysid = event['pathParameters']['sysid']
    resp = table.get_item(Key={'sysid': sysid})
    sys = resp.get('Item')
    
    if sys is None:
        return {
            'statusCode': 404
        }
    
    body = json.loads(event['body'])
    evidence_type = body.get('type')
    evidence = sys.get('evidence', [])
    if evidence_type == 'sbom':
        sbom = body['evidence']
        for component in sbom['components']:
            name = component['name'].lower().strip()
            if component['purl'].startswith('pkg:pypi'):
                package = pip_packages.get(name)
            elif component['purl'].startswith('pkg:npm'):
                package = npm_packages.get(name)
            else:
                package = None
            if package is not None:
                evidence.append({
                    'id': package['item'].split('/')[-1], 
                    'name': name,
                    'mention': component['name'],
                    'confidence': Decimal(1.),
                    'sourceType': 'sbom',
                    'source': body['name'],
                    'timestamp': now
                })
    
    elif evidence_type == 'document':
        doc = body['evidence']
        try:
            text = get_text_evidence(doc)
        except Exception:
            return {
                'statusCode': 500,
                'body': json.dumps({'message': 'failed to load evidence'})
            }
        doc = nlp(text)
        evidence += [{
            'id': ent['concept_id'], 
            'name': linker.kb.cui_to_entity[ent['concept_id']].canonical_name,
            'confidence': Decimal(ent['similarity']),
            'mention': ent['mention'],
            'sourceType': 'document', 
            'source': body['name'], 
            'timestamp': now
            } for ent in doc._.linked_entities]
    else:
        return {
            'statusCode': 400,
            'body': json.dumps({'message': f'evidence type {evidence_type} not supported'})
        }
    
    sys['evidence'] = evidence
    evidence = pandas.DataFrame(evidence)
    summary = evidence.groupby('id').agg({
        'mention': 'count',  
        'timestamp': 'max', 
        'confidence': 'max', 
        'source': lambda x: x.unique().tolist(),
        'name': 'first'
        }).reset_index().rename(columns={
            'mention': 'mention_count', 
            'timestamp': 'last_mentioned',
            'confidence': 'max_confidence',
            'source': 'sources'
        })
    
    summary['types'] = summary['id'].apply(get_entity_types)
    sys['components'] = summary.to_dict(orient='records')
    table.put_item(Item=sys)
    return {
        'statusCode': 200,
    }