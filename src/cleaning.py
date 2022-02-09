import re
from regex_patterns import REGEX_PARTY_PATTERN, REGEX_LAW_FIRM_PATTERN, REGEX_ET_AL


def get_list_of_matches(text, pattern):
    l = []
    for match in re.finditer(pattern, text):
        start, end = match.span()
        l.append(text[start:end])
    return l


def clean_party_names(text):
    for party in get_list_of_matches(text, REGEX_PARTY_PATTERN):
        text = text.replace(party, "Company" + party[6] + " ")
    return text


def clean_firm_names(text):
    for law_firm in get_list_of_matches(text, REGEX_LAW_FIRM_PATTERN):
        text = text.replace(law_firm, "Law_firm" + law_firm[5] + " ")
    return text


def clean_role_names(text):
    text = re.sub("([.,!:()])", "", text.lower())
    if text[-1] == "s":
        return text[:-1]
    else:
        return text


def replace_et_al(text):
    return re.sub(REGEX_ET_AL, "is", text)
