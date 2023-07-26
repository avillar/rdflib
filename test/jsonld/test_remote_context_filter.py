from __future__ import annotations

import json

import pytest

from rdflib import Graph, Literal, URIRef
from rdflib.plugins.shared.jsonld import context as jsonld_context

REMOTE = "https://example.com/ctx.jsonld"

DATA_TOP = {
    "@context": REMOTE,
    "@id": "http://example.com/res",
    "p": "x",
}

# Remote context referenced from a term-scoped context
DATA_SCOPED = {
    "@context": {
        "@version": 1.1,
        "ex": "http://example.com/",
        "nested": {"@id": "ex:nested", "@context": REMOTE},
    },
    "@id": "http://example.com/res",
    "nested": {"@id": "http://example.com/other", "p": "x"},
}


@pytest.fixture
def fake_remote(monkeypatch):
    fetched = []

    def source_to_json(source, *args, **kwargs):
        fetched.append(source)
        return {"@context": {"p": "http://example.com/p"}}, None

    monkeypatch.setattr(jsonld_context, "source_to_json", source_to_json)
    return fetched


def _parse(data, **kwargs):
    return Graph().parse(data=json.dumps(data), format="json-ld", **kwargs)


def test_no_filter_fetches(fake_remote):
    g = _parse(DATA_TOP)
    assert fake_remote == [REMOTE]
    assert (
        URIRef("http://example.com/res"),
        URIRef("http://example.com/p"),
        Literal("x"),
    ) in g


def test_filter_allows(fake_remote):
    g = _parse(DATA_TOP, remote_context_url_filter=lambda url: url == REMOTE)
    assert fake_remote == [REMOTE]
    assert len(g) == 1


@pytest.mark.parametrize("data", [DATA_TOP, DATA_SCOPED])
def test_filter_rejects(fake_remote, data):
    with pytest.raises(ValueError, match="not allowed"):
        _parse(data, remote_context_url_filter=lambda url: False)
    assert fake_remote == []
