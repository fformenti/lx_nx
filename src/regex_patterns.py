import re

# -------
# On Opinion2 firm2 and firm3 had incorrect patterns. The regex below is able to parse such errors.
# -------

REGEX_PARTY_PATTERN = re.compile(r"\{party\w_\}[^{]+\{[/]?party\w[_]?}")
REGEX_LAW_FIRM_PATTERN = re.compile(r"\{firm\d_\}[^{]+\{[/]?firm\d[_]?}")

REGEX_TREATED_PARTY = re.compile(r"Company[A-Z]")
REGEX_TREATED_LAW_FIRM = re.compile(r"Law_firm\d+")

REGEX_ET_AL = re.compile(r",?\s?et al.[,\s]")
