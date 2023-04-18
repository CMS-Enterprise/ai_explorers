# Ontology Generation

The `make_ontology.py` script creates the ontology files for the API from Wikidata.

The script uses the Wikidata Query Service and REST API to create the software related extract of Wikidata. Note this probably will take about an hour to run. It then uses `scispacy` to create a searchable index for the ontology which is used by the API for linking entities.

It will produce the following files that need to be copied into the `/tech-profile-api/api/evidence/model` directory for the API:
- `wikidata_software_kb.jsonl` - the Wikidata only software ontology file
- `combined_kb.jsonl` - the Wikidata + CMS alias list ontology file (this is the one used by the API which we index for linking)
- `index/` - directory with the linking index files:
    - `index/concept_aliases.json` - map of index position to alias
    - `index/nmslib_index.bin` - search index file
    - `index/tfdif_vectorizer.joblib` - TF-IDF vectorizer model
    - `index/tfidf_vectors_sparse.npz` - the TF-IDF-encoded aliases used to create the search index