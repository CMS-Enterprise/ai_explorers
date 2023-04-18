import json
import spacy
from text import EntityLinker

nlp = spacy.load('en_core_web_trf')
# nlp.add_pipe('entity-linker', config={'data_dir': '/opt/ml/model/', 'use_entities': True})
linker = EntityLinker(nlp, use_entities=True)
def lambda_handler(event, context):
    body = json.loads(event['body'])
    doc = nlp(body['text'])
    doc = linker(doc)
    return {
        'statusCode': 200,
        'body': json.dumps({'entities': doc._.linked_entities})
    }