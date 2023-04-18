from io import StringIO

from ghapi.core import GhApi, HTTP404NotFoundError
from markdown import Markdown
import pandas
import requests

def get_stackoverflow_wikidata():
    with open('wikidata_stackoverflow_query.sparql') as f:
        query = f.read()
        
    response = requests.get(
        'https://query.wikidata.org/sparql',
        params={
            'format': 'json',
            'query': query
        }
    )
    
    tagged_entities = pandas.json_normalize(response.json()['results']['bindings'])
    tagged_entities = tagged_entities[['item.value', 'article.value', 'seTag.value', 'parentLabel.value']]
    tagged_entities.columns = [col.split('.')[0] for col in tagged_entities.columns]
    tagged_entities['item'] = tagged_entities['item'].apply(lambda x: x.split('/')[-1])
    tagged_entities = tagged_entities[tagged_entities['seTag'].str.startswith('https://stackoverflow.com/tags/')]
    tagged_entities['seTag'] = tagged_entities['seTag'].apply(lambda x: x.split('/')[-1])
    tagged_entities = tagged_entities[['item', 'seTag']].drop_duplicates().set_index('item')
    return tagged_entities

def unmark_element(element, stream=None):
    if stream is None:
        stream = StringIO()
    if element.text:
        stream.write(element.text)
    for sub in element:
        unmark_element(sub, stream)
    if element.tail:
        stream.write(element.tail)
    return stream.getvalue()


# patching Markdown
Markdown.output_formats["plain"] = unmark_element
__md = Markdown(output_format="plain")
__md.stripTopLevelTags = False


def unmark(text):
    return __md.convert(text)

def get_readme(owner, repo):
    api = GhApi(owner=owner, repo=repo)
    try:
        content = api.get_content('README.md')
    except HTTP404NotFoundError:
        print("Could not find README.md in {repo}")
    content = content.decode('utf-8')
    return unmark(content)