import pandas
import requests
import time 
from multiprocessing.dummy import Pool
from wikidata.client import Client
from scispacy.candidate_generation import create_tfidf_ann_index
from scispacy.linking_utils import KnowledgeBase

url = 'https://query.wikidata.org/sparql'
query = '''SELECT ?item ?itemLabel 
WHERE 
{
  ?item wdt:P31 wd:Q17155032. # Instance of Software Category
  SERVICE wikibase:label { bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en". } # Helps get the label in your language, if not, then en language
}'''

r = requests.get(url, params = {'format': 'json', 'query': query})
data = r.json()

cats = pandas.json_normalize(data['results']['bindings'])

entities = pandas.DataFrame()
for _, cat in cats.iterrows():
    start = time.time()
    qid = cat['item.value'].split('/')[-1]
    print(qid)
    query_chunk = f"""
    SELECT ?item ?itemLabel ?property ?value ?valueLabel WHERE {{
      VALUES (?property) {{
        (wdt:P31)
        (wdt:P279)
        (wdt:P366)
        (wdt:P178)
        (wdt:P8262)
        (wdt:P5568)
      }}
      ?item (wdt:P279|wdt:P31)/wdt:P279* wd:{qid} .
      ?item ?property ?value . 
      SERVICE wikibase:label {{ bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en". }}
    }}

    """
    r = requests.get(url, headers={'User-Agent': 'Software Ontology Builder (mhill92@gmail.com)'}, params = {'format': 'json', 'query': query_chunk})
    data = r.json()
    end = time.time()
    df = pandas.json_normalize(data['results']['bindings'])
    if df.empty:
        continue
    df = df[['item.value', 'itemLabel.value', 'property.value', 'valueLabel.value', 'value.value']]
    df['item.value'] = df['item.value'].apply(lambda x: x.split('/')[-1])
    df['value.value'] = df['value.value'].apply(lambda x: x.split('/')[-1])
    df['property.value'] = df['property.value'].apply(lambda x: x.split('/')[-1])
    entities = pandas.concat([entities, df]).drop_duplicates()

# Use the Wikidata REST API to get definition/alias
client = Client()
def get_wd(q_id):
    ent = client.get(q_id, load=True)
    return {
        'canonical_name': ent.attributes.get('labels', {}).get('en', {}).get('value', ''),
        'definition': ent.attributes.get('descriptions', {}).get('en', {}).get('value', ''),
        'aliases': [al.get('value', '') for al in ent.attributes.get('aliases', {}).get('en', [])]
    }

# This may take ~1 hour
q_values = entities['item.value'].value_counts().index.tolist()
with Pool(10) as p:
    data = list(tqdm.tqdm(p.imap(get_wd, q_values), total=len(q_values)))

    
entity_types = entities.groupby('item.value').apply(lambda x: x['valueLabel.value'].tolist())
wikidata_kb = pandas.DataFrame(data, index=q_values).join(
    entity_types.rename('types')).reset_index().rename(
    columns={'index':'concept_id'}
)

wikidata_kb.to_json('wikidata_software_kb.jsonl', orient='records', lines=True)


with open('cms_data/aliases.json') as f:
    cms_aliases = json.load(f)
    
cms_kb = pandas.DataFrame([{
    'concept_id': f'CMS{i:05d}', 'canonical_name': k, 'aliases': v, 'types': [], 'definition': ''} for i, (k, v) in enumerate(cms_aliases.items())])

wikidata_kb = pandas.read_json('wikidata_software_kb.jsonl', lines=True)
pandas.concat([wikidata_kb, cms_kb]).to_json('combined_kb.jsonl', lines=True, orient='records')

kb = KnowledgeBase('combined_kb.jsonl')
create_tfidf_ann_index('index/', kb)