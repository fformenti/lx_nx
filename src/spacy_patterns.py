SPACY_NER_PATTERNS = [
    {
        "label": "LP-A",
        "pattern": [
            {"LOWER": {"REGEX": "plaintiff|plaintiffs|appellant|petitioner"}},
            {"IS_PUNCT": True, "OP": "*"},
        ],
    },
    {
        "label": "LP-A",
        "pattern": [
            {"LOWER": "counter"},
            {"ORTH": "-", "OP": "?"},
            {"IS_SPACE": True, "OP": "?"},
            {"LOWER": "defendant"},
            {"IS_PUNCT": True, "OP": "*"},
        ],
    },
    {
        "label": "LP-D",
        "pattern": [
            {"LOWER": {"REGEX": "defendant|defendants|appellee|respondent"}},
            {"IS_PUNCT": True, "OP": "*"},
        ],
    },
    {
        "label": "LP-D",
        "pattern": [
            {"LOWER": "counter"},
            {"ORTH": "-", "OP": "?"},
            {"IS_SPACE": True, "OP": "?"},
            {"LOWER": {"REGEX": "plaintiff|plaintiffs|claimant|claimants"}},
            {"IS_PUNCT": True, "OP": "*"},
        ],
    },
    {
        "label": "LP-D",
        "pattern": [
            {"LOWER": "defendant"},
            {"ORTH": "-", "OP": "?"},
            {"IS_SPACE": True, "OP": "?"},
            {"LOWER": "intervenor"},
            {"IS_PUNCT": True, "OP": "+"},
        ],
    },
]
