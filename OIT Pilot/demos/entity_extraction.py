import pandas
import spacy  # version 3.0.6'

# initialize language model
nlp = spacy.load("en_core_web_md")

# add pipeline (declared through entry_points in setup.py)
nlp.add_pipe("entityLinker", last=True)

def extract_entities(text, tagged_entities=None):        
    doc = nlp(text)
    ents = []

    # iterates over sentences and extracted linked entities
    for sent in doc.sents:
        for ent in sent._.linkedEntities:
            ents.append({
                'text': ent.get_span().text,
                'label': ent.label,
                'description': ent.description,
                'wikidata_id': ent.get_url().split('/')[-1],
                'superclasses': [{
                    'wikidata_id': ent.get_url().split('/')[-1], 
                    'label': ent.label
                } for ent in ent.get_super_entities()]
            })
    if tagged_entities is not None:
        ents = pandas.DataFrame(ents).join(tagged_entities, on='wikidata_id').dropna(subset=['seTag'])
        ents = ents.drop_duplicates(subset=['text', 'wikidata_id'])
    return ents