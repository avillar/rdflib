from __future__ import annotations

import json

import pytest

from rdflib import Graph, Literal, URIRef


@pytest.mark.parametrize(
    ("raw_id", "expected"),
    [
        (1, "http://example.com/res/1"),
        (1.5, "http://example.com/res/1.5"),
    ],
)
def test_non_string_id(raw_id, expected):
    data = {
        "@context": {"@base": "http://example.com/res/", "p": "http://example.com/p"},
        "@id": raw_id,
        "p": "x",
    }
    g = Graph().parse(data=json.dumps(data), format="json-ld")
    assert set(g) == {(URIRef(expected), URIRef("http://example.com/p"), Literal("x"))}


def test_non_string_nested_id():
    data = {
        "@context": {"@base": "http://example.com/res/", "p": "http://example.com/p"},
        "@id": "parent",
        "p": {"@id": 2},
    }
    g = Graph().parse(data=json.dumps(data), format="json-ld")
    assert (
        URIRef("http://example.com/res/parent"),
        URIRef("http://example.com/p"),
        URIRef("http://example.com/res/2"),
    ) in g


def test_boolean_id_not_converted():
    data = {
        "@context": {"@base": "http://example.com/res/", "p": "http://example.com/p"},
        "@id": True,
        "p": "x",
    }
    g = Graph().parse(data=json.dumps(data), format="json-ld")
    assert len(g) == 1
    assert not any(
        isinstance(s, URIRef) and str(s).endswith("True") for s in g.subjects()
    )
