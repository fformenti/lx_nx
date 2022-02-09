import spacy
from spacy_patterns import SPACY_NER_PATTERNS
from custom_component import law_firm_ner, party_ner, set_custom_boundaries

# python -m spacy download en_core_web_lg

nlp = spacy.load("en_core_web_sm", disable=["ner"])
nlp.add_pipe("set_custom_boundaries", before="parser")

ruler = nlp.add_pipe("entity_ruler")
ruler.add_patterns(SPACY_NER_PATTERNS)

nlp.add_pipe("party_ner", after="entity_ruler")
nlp.add_pipe("law_firm_ner", after="party_ner")
