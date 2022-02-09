import itertools

import pandas as pd

from cleaning import (
    clean_firm_names,
    clean_party_names,
    clean_role_names,
    replace_et_al,
)
from pipeline_creation import nlp

TABLE_FIELDS = [
    "Opinion",
    "Party Letter",
    "Party name",
    "Party type(s) - Annotated",
    "Law firm(s) - Annotated",
]

SIDE_POINTS = {"LP-D": -1, "LP-A": 1}


def read_opinion_txt(path):
    with open(path, "r") as myfile:
        full_doc_list = myfile.read().splitlines()
    return full_doc_list


def clean_opinion_txt(full_doc_list):
    full_doc_list = [clean_party_names(text) for text in full_doc_list]
    full_doc_list = [clean_firm_names(text) for text in full_doc_list]
    full_doc_list = [replace_et_al(text) for text in full_doc_list]
    return full_doc_list


def get_nodes_and_edges(full_doc_list):
    party_roles_list = []
    firm_roles_list = []
    party_party_list = []
    firm_firm_list = []
    party_firms_list = []
    all_parties = set()
    all_firms = set()
    for line_text in full_doc_list:
        line_doc = nlp(line_text)
        sents = line_doc.sents
        for sent in sents:
            party_ents = [ent.text for ent in sent.ents if ent.label_ == "PARTY"]
            all_parties = all_parties.union(set(party_ents))
            firm_ents = [ent.text for ent in sent.ents if ent.label_ == "LAW_FIRM"]
            all_firms = all_firms.union(set(firm_ents))
            roles_ents = [
                (clean_role_names(ent.text), ent.label_, SIDE_POINTS[ent.label_])
                for ent in sent.ents
                if ent.label_[:2] == "LP"
            ]
            for p, r in itertools.product(*[party_ents, roles_ents]):
                party_roles_list.append([p, r[0], r[1], r[2]])

            for p1, p2 in itertools.product(*[party_ents, party_ents]):
                if p1 != p2:
                    party_party_list.append([p1, p2])

            for f, r in itertools.product(*[firm_ents, roles_ents]):
                firm_roles_list.append([f, r[0], r[1], r[2]])

            for f1, f2 in itertools.product(*[firm_ents, firm_ents]):
                if f1 != f2:
                    firm_firm_list.append([f1, f2])

            for p, f in itertools.product(*[party_ents, firm_ents]):
                party_firms_list.append([p, f])
    return {
        "edges": {
            "party_roles_list": party_roles_list,
            "party_party_list": party_party_list,
            "firm_roles_list": firm_roles_list,
            "firm_firm_list": firm_firm_list,
            "party_firms_list": party_firms_list,
        },
        "nodes": {"all_parties": all_parties, "all_firms": all_firms},
    }


def make_nodes_scores(nodes_edges):
    all_parties = nodes_edges["nodes"]["all_parties"]
    all_firms = nodes_edges["nodes"]["all_firms"]

    party_roles_list = nodes_edges["edges"]["party_roles_list"]
    firm_roles_list = nodes_edges["edges"]["firm_roles_list"]
    party_party_list = nodes_edges["edges"]["party_party_list"]
    party_firms_list = nodes_edges["edges"]["party_firms_list"]
    firm_firm_list = nodes_edges["edges"]["firm_firm_list"]

    party_roles_full = pd.DataFrame(
        party_roles_list, columns=["party", "party_role", "side", "points"]
    )
    if len(party_roles_full) > 0:
        party_points = party_roles_full.groupby(["party"], as_index=False)[
            "points"
        ].sum()
    else:
        party_points = pd.DataFrame({"party": [], "points": []})

    firm_roles_full = pd.DataFrame(
        firm_roles_list, columns=["firm", "firm_role", "side", "points"]
    )
    if len(firm_roles_full) > 0:
        firm_points = firm_roles_full.groupby(["firm"], as_index=False)["points"].sum()
    else:
        firm_points = pd.DataFrame({"firm": [], "points": []})

    score_table = pd.concat(
        [
            party_points.rename(columns={"party": "node"}),
            firm_points.rename(columns={"firm": "node"}),
        ]
    )
    ref_points_node = list(score_table["node"])
    missing_nodes = [
        node
        for node in all_parties.difference(set(ref_points_node)).union(
            all_firms.difference(set(ref_points_node))
        )
    ]

    score_table.set_index("node", inplace=True)
    nodes_scores = score_table.to_dict()["points"]

    new_scores = {node: 0 for node in missing_nodes}
    for node in missing_nodes:
        aux = 0
        for node1, node2 in party_party_list + party_firms_list + firm_firm_list:
            if node1 == node or node == node2:
                points1 = int(
                    0 if nodes_scores.get(node1) is None else nodes_scores.get(node1)
                )
                points2 = int(
                    0 if nodes_scores.get(node2) is None else nodes_scores.get(node2)
                )
                aux += points1 + points2
        new_scores[node] = aux
    return {**nodes_scores, **new_scores}


def make_side_tables(points_dict):
    party_side_list = []
    firm_side_list = []
    for k, v in points_dict.items():
        node_side = {}

        node_side["points"] = v
        if v > 0:
            node_side["side"] = "LP-A"
        elif v == 0:
            node_side["side"] = "LP-N"
        else:
            node_side["side"] = "LP-D"

        if k[0:3] == "Law":
            node_side["firm"] = k
            firm_side_list.append(node_side)
        else:
            node_side["party"] = k
            party_side_list.append(node_side)

    return pd.DataFrame(party_side_list), pd.DataFrame(firm_side_list)


def remove_wrong_party_roles(party_roles_list, party_side_df):

    party_roles_full = pd.DataFrame(
        party_roles_list, columns=["party", "party_role", "side", "points"]
    )

    party_roles = party_roles_full.merge(
        party_side_df, how="inner", on=["party", "side"]
    )
    if len(party_roles) > 0:
        summary_party_roles = (
            party_roles.groupby(["party", "side"])["party_role"]
            .apply(list)
            .reset_index()
        )
    else:
        summary_party_roles = pd.DataFrame({"party": [], "side": [], "party_role": []})
    return summary_party_roles


def remove_wrong_firm_roles(firm_roles_list, firm_side_df):
    firm_roles_full = pd.DataFrame(
        firm_roles_list, columns=["firm", "firm_role", "side", "points"]
    )

    firm_roles = firm_roles_full.merge(firm_side_df, how="inner", on=["firm", "side"])
    if len(firm_roles) > 0:
        summary_firm_roles = (
            firm_roles.groupby(["firm", "side"])["firm_role"].apply(list).reset_index()
        )
    else:
        summary_firm_roles = pd.DataFrame({"firm": [], "side": [], "firm_role": []})
    return summary_firm_roles


def make_party_firm_table(
    party_firms_list, party_side_df, firm_side_df, party_roles, firm_roles
):
    if len(party_firms_list) > 0:
        party_firms = pd.DataFrame(party_firms_list, columns=["party", "firm"])
        party_firms = party_firms.merge(party_side_df, how="left", on=["party"])
        party_firms = party_firms.merge(
            firm_side_df, how="left", on="firm", suffixes=("_party", "_firm")
        )
        party_firms["keep"] = party_firms["points_party"] * party_firms["points_firm"]
        party_firms = party_firms[party_firms["keep"] >= 0]
        party_firms = party_firms.merge(party_roles, how="left", on="party")
        party_firms = party_firms.merge(firm_roles, how="left", on="firm")
    else:
        party_firms = party_roles.merge(firm_roles, how="inner", on="side")

    party_firms["party_role"] = party_firms["party_role"].apply(
        lambda d: d if isinstance(d, list) else []
    )
    party_firms["firm_role"] = party_firms["firm_role"].apply(
        lambda d: d if isinstance(d, list) else []
    )
    party_firms["role"] = party_firms.apply(
        lambda x: x["party_role"] + x["firm_role"], axis=1
    )
    party_firms["firm"] = party_firms["firm"].apply(lambda x: [x[-1]])
    return party_firms


def make_opinion_table(party_firms, opinion_idx):
    opinion_summary = party_firms.groupby("party", as_index=False)["firm", "role"].sum()
    opinion_summary["firm"] = opinion_summary["firm"].apply(lambda x: set(x))
    opinion_summary["role"] = opinion_summary["role"].apply(lambda x: set(x))
    opinion_summary["Opinion"] = opinion_idx
    opinion_summary["party"] = opinion_summary["party"].apply(lambda x: x[-1])
    opinion_summary.rename(columns={"party": "Party Letter"}, inplace=True)
    opinion_summary["Party type(s) - Modeled"] = opinion_summary["role"].apply(
        lambda x: x if isinstance(x, float) else ",".join(x)
    )
    opinion_summary["Law firm(s) - Model"] = opinion_summary["firm"].apply(
        lambda x: x if isinstance(x, float) else ",".join(x)
    )
    return opinion_summary.drop(columns=["firm", "role"], inplace=False)


def summarize_opinion(opinion_idx):

    full_doc_list = read_opinion_txt(path=f"../data/input/Opinion{opinion_idx}.txt")
    full_doc_list = clean_opinion_txt(full_doc_list)

    nodes_edges = get_nodes_and_edges(full_doc_list)
    nodes_scores = make_nodes_scores(nodes_edges)
    party_side_df, firm_side_df = make_side_tables(nodes_scores)

    party_firms_list = nodes_edges["edges"]["party_firms_list"]
    party_roles_list = nodes_edges["edges"]["party_roles_list"]
    firm_roles_list = nodes_edges["edges"]["firm_roles_list"]

    party_roles = remove_wrong_party_roles(party_roles_list, party_side_df)
    firm_roles = remove_wrong_firm_roles(firm_roles_list, firm_side_df)

    party_firms = make_party_firm_table(
        party_firms_list, party_side_df, firm_side_df, party_roles, firm_roles
    )

    return make_opinion_table(party_firms, opinion_idx)


if __name__ == "__main__":

    table = pd.read_csv("../data/input/data.csv", sep=",", usecols=TABLE_FIELDS)
    opinions = set(table["Opinion"])
    full_summary_list = []
    for opinion_idx in opinions:
        print(opinion_idx)
        full_summary_list.append(summarize_opinion(opinion_idx))
    full_summary = pd.concat(full_summary_list)
    ouput_table = table.merge(full_summary, how="left", on=["Opinion", "Party Letter"])
    ouput_table.to_csv("../data/output/output2.csv", index=False)
