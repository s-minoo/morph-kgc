__author__ = "Julián Arenas-Guerrero"
__license__ = "Apache-2.0"

"""
Stage 5 — Triple Assembly
==========================
Combines subject / predicate / object columns into a single ``triple`` string
and optionally appends the graph component for N-Quads output.

Public API
----------
assemble_triples(data, rule, rml_mapping, config, nest_level=0) -> pd.DataFrame
"""

import pandas as pd

from ...constants import (
    RML_TEMPLATE, RML_CONSTANT, RML_REFERENCE, RML_EXECUTION,
    RML_IRI, RML_DEFAULT_GRAPH, NQUADS,
)
from ...mapping.model import RMLRule, RMLMapping
from .terms import _apply_template, _apply_fnml


def resolve_graph(
    data: pd.DataFrame,
    rule: RMLRule,
    rml_mapping: RMLMapping,
    config,
    nest_level: int = 0,
) -> pd.DataFrame:
    """
    Write the graph term of *rule* into ``data['_graph']``.
    The default graph (or no graph map) yields an empty string.
    """
    if nest_level == 0 and config.output_format == NQUADS:
        gm = rule.graph
        if (
            gm
            and gm.map_type in (RML_TEMPLATE, RML_CONSTANT, RML_REFERENCE)
            and gm.map_value != RML_DEFAULT_GRAPH
        ):
            data = _apply_template(
                data, gm.map_value, gm.map_type, config, "_graph", termtype=RML_IRI
            )
        elif gm and gm.map_type == RML_EXECUTION:
            data = _apply_fnml(
                data, gm.map_value, rml_mapping, config, "_graph", termtype=RML_IRI
            )
        else:
            data["_graph"] = ""
    return data

def concatenate_terms(data: pd.DataFrame) -> pd.DataFrame:
    """
    Write ``data['triple']`` as ``subject predicate object``, followed by the
    graph term when a ``_graph`` column is present, and drop those columns.
    """
    data["triple"] = data["subject"] + " " + data["predicate"] + " " + data["object"]
    if "_graph" in data.columns:
        data["triple"] = data["triple"] + " " + data["_graph"]
    return data.drop(
        columns=["subject", "predicate", "object", "_graph"], errors="ignore"
    )

def assemble_triples(
    data: pd.DataFrame,
    rule: RMLRule,
    rml_mapping: RMLMapping,
    config,
    nest_level: int = 0,
) -> pd.DataFrame:
    """
    Write ``data['triple']`` as ``subject predicate object``.
    At nest_level 0 with N-Quads output, also appends the graph term.
    Drops the individual subject/predicate/object columns afterwards.
    """

    data = resolve_graph(data, rule, rml_mapping, config, nest_level)
    return concatenate_terms(data)
