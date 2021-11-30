# Generated query language
LANGUAGE = "sparql"

# Encoding config
DEFAULT_ENCODING = "utf-8"

# Sparql config
SPARQL_PREAMBLE = u"""
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX foaf: <http://xmlns.com/foaf/0.1/>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
PREFIX quepy: <http://www.machinalis.com/quepy#>
PREFIX dbpedia: <http://dbpedia.org/ontology/>
PREFIX dbpprop: <http://dbpedia.org/property/>
PREFIX dbpedia-owl: <http://dbpedia.org/ontology/>
PREFIX category: <http://opendata.aragon.es/def/ei2a/categorization#>
PREFIX locn: <http://www.w3.org/ns/locn#>
PREFIX time: <http://www.w3.org/2006/time#>
PREFIX ei2a: <http://opendata.aragon.es/def/ei2a#>
PREFIX person: <http://www.w3.org/ns/person#>
PREFIX org: <http://www.w3.org/ns/org#>
"""
