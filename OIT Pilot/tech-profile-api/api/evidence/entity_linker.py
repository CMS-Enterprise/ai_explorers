import os

import json
import joblib
import numpy as np
import nmslib
from sentence_transformers import SentenceTransformer, util
from spacy.tokens import Doc, Span
from spacy.language import Language
from spacy_entity_linker.TermCandidateExtractor import TermCandidateExtractor
from scispacy.candidate_generation import CandidateGenerator
from scispacy.linking_utils import KnowledgeBase
import scipy

def candidates_to_dict(candidates, mention):
    dict_candidates = []
    for cand in candidates:
        best_alias = np.argmax(cand.similarities)
        dict_candidates.append({
            'concept_id': cand.concept_id,
            'similarity': cand.similarities[best_alias],
            'alias': cand.aliases[best_alias],
            'mention': mention
        })
    return dict_candidates

def load_candidate_generator(tfidfs_vector_path, tfidfs_vectorizer_path, ann_index_path, alias_path, kb):
        concept_alias_tfidfs = scipy.sparse.load_npz(tfidfs_vector_path).astype(np.float32)
        tfidf_vectorizer = joblib.load(tfidfs_vectorizer_path)
        ann_index = nmslib.init(
            method="hnsw",
            space="cosinesimil_sparse",
            data_type=nmslib.DataType.SPARSE_VECTOR,
        )
        ann_index.addDataPointBatch(concept_alias_tfidfs)
        ann_index.loadIndex(ann_index_path)
        query_time_params = {"efSearch": 200}
        ann_index.setQueryTimeParams(query_time_params)
        with open(alias_path) as f:
            ann_concept_aliases_list = json.load(f)
        
        return CandidateGenerator(ann_index, tfidf_vectorizer, ann_concept_aliases_list, kb)


@Language.factory('entity-linker')
class EntityLinker:
    def __init__(self, nlp=None, name="entity-linker", data_dir='/opt/ml/model', use_entities=False):
        Doc.set_extension('linked_entities', default=[], force=True)
        Span.set_extension('linked_entities', default=None, force=True)

        self.use_entities = use_entities
        self.kb = KnowledgeBase(os.path.join(data_dir, 'combined_kb.jsonl'))
        self.candidate_generator = load_candidate_generator(
            os.path.join(data_dir, 'tfidf_vectors_sparse.npz'),
            os.path.join(data_dir, 'tfidf_vectorizer.joblib'),
            os.path.join(data_dir, 'nmslib_index.bin'),
            os.path.join(data_dir, 'concept_aliases.json'),
            self.kb
        )
        self.context_model = SentenceTransformer(os.path.join(data_dir, 'all-MiniLM-L6-v2'), device='cpu')

    def __call__(self, doc):
        if self.use_entities:
            candidate_terms = [[ent] for ent in doc.ents]
        else:
            tce = TermCandidateExtractor(doc)
            candidate_terms = [term.variations for term in tce]

        entities = []
        for term in candidate_terms:
            var_candidates = self.candidate_generator([var.text for var in term], k=10)
            batch = []
            for mention, candidates in zip(term, var_candidates):
                batch += candidates_to_dict(candidates, mention)
            sentences = [candidate['alias'] + ', ' + self.kb.cui_to_entity[candidate['concept_id']].definition for candidate in batch]
            mention = [term[0].sent.text]
            mention_vect = self.context_model.encode(mention)
            sent_vect = self.context_model.encode(sentences)
            sim = util.cos_sim(mention_vect, sent_vect)[0]
            for i, cand in enumerate(batch):
                cand['context_sim'] = float(sim[i])
                cand['exact_match'] = 0. if self.kb.alias_to_cuis.get(cand['mention']) is None else 1.
                cand['mention'] = cand['mention'].text
            batch.sort(key=lambda x: (x['exact_match'], x['similarity'], x['context_sim']), reverse=True)
            entities.append(batch[0])
        doc._.linked_entities = entities
        return doc