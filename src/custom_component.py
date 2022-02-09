import re

from spacy.language import Language
from spacy.tokens import Span
from spacy.util import filter_spans

from regex_patterns import (
    REGEX_LAW_FIRM_PATTERN,
    REGEX_PARTY_PATTERN,
    REGEX_TREATED_PARTY,
    REGEX_TREATED_LAW_FIRM,
)


@Language.component("set_custom_boundaries")
def set_custom_boundaries(doc):
    for token in doc[:-1]:
        if token.text in ["v.", "against"]:
            doc[token.i + 1].is_sent_start = True
    return doc


@Language.component(("party_ner"))
def party_ner(doc):
    original_ents = list(doc.ents)

    mwt_ents = []
    for match in re.finditer(REGEX_TREATED_PARTY, doc.text):
        start, end = match.span()
        span = doc.char_span(start, end)
        if span is not None:
            mwt_ents.append((span.start, span.end, span.text))

    for ent in mwt_ents:
        start, end, _ = ent
        per_ent = Span(doc, start, end, label="PARTY")
        original_ents.append(per_ent)

    filtered = filter_spans(original_ents)
    doc.ents = filtered
    return doc


@Language.component(("law_firm_ner"))
def law_firm_ner(doc):
    original_ents = list(doc.ents)

    mwt_ents = []
    for match in re.finditer(REGEX_TREATED_LAW_FIRM, doc.text):
        start, end = match.span()
        span = doc.char_span(start, end)
        if span is not None:
            mwt_ents.append((span.start, span.end, span.text))

    for ent in mwt_ents:
        start, end, _ = ent
        per_ent = Span(doc, start, end, label="LAW_FIRM")
        original_ents.append(per_ent)

    filtered = filter_spans(original_ents)
    doc.ents = filtered
    return doc


# @Language.component(("fix_litigation_roles"))
# def fix_litigation_roles(doc):

#     roles_ents = [ent for ent in doc.ents if ent.label_[0:2]=="LP"]

#     mwt_ents = []
#     for match in re.finditer(REGEX_TREATED_LAW_FIRM, doc.text):
#         start, end = match.span()
#         span = doc.char_span(start, end)
#         if span is not None:
#             mwt_ents.append((span.start, span.end, span.text))

#     for ent in mwt_ents:
#         start, end, _ = ent
#         per_ent = Span(doc, start, end, label="LAW_FIRM")
#         original_ents.append(per_ent)

#     filtered = filter_spans(original_ents)
#     doc.ents = filtered
#     return doc
