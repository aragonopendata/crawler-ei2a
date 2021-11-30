import json
import urllib.parse
import urllib.request

VIRTUOSO_URL = "http://argon-virtuoso:8890/sparql/"

PREFIXES = [("rdf", "http://www.w3.org/1999/02/22-rdf-syntax-ns#"),("person", "http://www.w3.org/ns/person#"),
            ("org", "http://www.w3.org/ns/org#"),("ei2a", "http://opendata.aragon.es/def/ei2a#"),
            ("time", "http://www.w3.org/2006/time#"),("locn","http://www.w3.org/ns/locn#"),
            ("owl","http://www.w3.org/2002/07/owl#"),("category","http://opendata.aragon.es/def/ei2a/categorization#"),
            ("rdfs", "http://www.w3.org/2000/01/rdf-schema#")]

def sparqlQuery(query, baseURL, format="application/json"):
    params={
        "default-graph": "http://opendata.aragon.es/def/ei2a",
        "should-sponge": "soft",
        "query": query,
        "debug": "on",
        "timeout": "",
        "format": format,
        "save": "display",
        "fname": ""
    }
    querypart=urllib.parse.urlencode(params).encode("utf-8")
    response = urllib.request.urlopen(baseURL,querypart).read()
    if format == "application/json":
        return json.loads(response)['results']['bindings']
    else:
        return response.decode("utf-8")

def get_variable_name(property,i):
    if ":" in property and property.split(":")[1]:
        varialbeProperty = property.split(":")[1]
    else:
        varialbeProperty = "variable" + str(i)
    return varialbeProperty

# Replace prefixes to build the query
def replace_prefixes(string):
    for (prefix, url) in PREFIXES:
        string = string.replace(url, prefix + ":")
    return string

# Get prefixes header of the query
def get_prefixes():
    aux = ""
    for (prefix, url) in PREFIXES:
        aux += "PREFIX " + prefix + ": <" + url + "> "
    return aux

# Get the concept with the prefixes replaced or quoted if it is a string
def convert_concept(concept):
    conceptAux = replace_prefixes(concept)
    if conceptAux == concept:
        return "'" + concept + "'"
    else:
        return conceptAux
