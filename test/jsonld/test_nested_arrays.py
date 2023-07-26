# -*- coding: UTF-8 -*-
import sys

from rdflib.collection import Collection

from rdflib import *
from rdflib.plugin import Parser, register

register("json-ld", Parser, "rdflib.plugins.parsers.jsonld", "JsonLDParser")
register("application/ld+json", Parser, "rdflib.plugins.parsers.jsonld", "JsonLDParser")

prop = URIRef("http://example.com/props/a")

data = """
{
    "@context": {
        "a": {
            "@id": "_PROP_ID_",
            "@container": "@list"
        }
    },
    "a": [
        [[1, 2, 3], ["4", 5]],
        6,
        [7, { "@id": "http://example.com/res" }]
    ]
}
""".replace('_PROP_ID_', str(prop))


def test_graph():
    g = Graph()
    g.parse(data=data, format="application/ld+json")

    outer = Collection(g, next(g.objects(predicate=prop)))
    inner1, inner2, inner3 = outer

    inner1 = Collection(g, inner1)
    inner1_1, inner1_2 = map(lambda l: Collection(g, l), inner1)
    assert list(inner1_1) == [Literal(x) for x in (1, 2, 3)]
    assert list(inner1_2) == [Literal(x) for x in ("4", 5)]

    assert inner2 == Literal(6)

    inner3 = Collection(g, inner3)
    assert list(inner3) == [Literal(7), URIRef("http://example.com/res")]
