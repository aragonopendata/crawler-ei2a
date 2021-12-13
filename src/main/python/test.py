import logging
from urllib.parse import urljoin
from urllib.parse import urlparse
import sparqlhelper
import csv

import config as cfg

def query1():
    query="PREFIX schema: <http://schema.org/>   PREFIX rdf:<http://www.w3.org/1999/02/22-rdf-syntax-ns#> PREFIX owl:<http://www.w3.org/2002/07/owl#> PREFIX ei2a:<http://opendata.aragon.es/def/ei2av2#> PREFIX locn: <http://www.w3.org/ns/locn#> PREFIX dc: <http://purl.org/dc/elements/1.1/title#>"
    query += "  SELECT ?urlID  group_concat(distinct ?p ;separator='; ') as ?personas WHERE { "
    query += " select ?urlID  group_concat(distinct ?nombre;separator='; ') as ?p"
    query += " where { "
    query += " ?urlID rdf:type schema:CreativeWork . "
    query += " ?urlID rdf:type owl:NamedIndividual . "
    query += " ?urlID schema:concept ?nti . "
    query += " ?urlID schema:about ?ent1 ."
    query += " ?ent1 <http://www.w3.org/1999/02/22-rdf-syntax-ns#type>  <http://xmlns.com/foaf/0.1/Person> . " 
    query += " ?ent1 <http://xmlns.com/foaf/0.1/name> ?nombre "
    query += " } "
    query += " group by ?urlID }"
    print(sparqlhelper.SparqlHelper.query_csv(cfg.sparql_user,cfg.sparql_pass,cfg.sparql_server,cfg.sparql_path_auth,'?default-graph-uri=&format=csv&should-sponge=&timeout=0&signal_void=on',query))


def query2():
    query="PREFIX schema: <http://schema.org/>   PREFIX rdf:<http://www.w3.org/1999/02/22-rdf-syntax-ns#> PREFIX owl:<http://www.w3.org/2002/07/owl#> PREFIX ei2a:<http://opendata.aragon.es/def/ei2av2#> PREFIX locn: <http://www.w3.org/ns/locn#> PREFIX dc: <http://purl.org/dc/elements/1.1/title#>"
    query += "  SELECT ?urlID  group_concat(distinct ?o ;separator='; ') as ?organizaciones  group_concat(distinct ?p ;separator='; ') as ?personas group_concat(distinct ?l;separator='; ') as ?location "
    query += "   group_concat(distinct ?u;separator='; ') as ?url  group_concat(distinct ?t;separator='; ') as ?t  group_concat(distinct ?nti;separator='; ') as ?nti WHERE { " 
    query += " { "
    query += "    select ?urlID  group_concat(distinct ?loc;separator='; ') as ?l"
    query += "    where { "
    query += "    ?urlID rdf:type schema:CreativeWork . "
    query += "    ?urlID rdf:type owl:NamedIndividual . "
    query += "    ?urlID schema:concept ?nti . "
    query += "    ?urlID schema:about ?ent1 ."
    query += "    ?ent1 <http://www.w3.org/1999/02/22-rdf-syntax-ns#type>  <http://dbpedia.org/ontology/GovernmentalAdministrativeRegion> . "
    query += "    ?ent1 <http://www.w3.org/2000/01/rdf-schema#label> ?loc"
    query += "   }  "
    query += " group by ?urlID } "
    query += " union  { "
    query += "    select ?urlID  group_concat(distinct ?org;separator='; ') as ?o"
    query += "    where { "
    query += "    ?urlID rdf:type schema:CreativeWork . "
    query += "    ?urlID rdf:type owl:NamedIndividual . "
    query += "    ?urlID schema:concept ?nti . "
    query += "    ?urlID schema:about ?ent1 ."
    query += "    ?ent1 <http://www.w3.org/1999/02/22-rdf-syntax-ns#type>   <http://www.w3.org/ns/org#Organization>. "
    query += "    ?ent1 <http://purl.org/dc/elements/1.1/title> ?org "
    query += "   }  "
    query += " group by ?urlID } "
    query += " union  { "
    query += " select ?urlID  group_concat(distinct ?nombre;separator='; ') as ?p"
    query += " where { "
    query += " ?urlID rdf:type schema:CreativeWork . "
    query += " ?urlID rdf:type owl:NamedIndividual . "
    query += " ?urlID schema:concept ?nti . "
    query += " ?urlID schema:about ?ent1 ."
    query += " ?ent1 <http://www.w3.org/1999/02/22-rdf-syntax-ns#type>  <http://xmlns.com/foaf/0.1/Person> . " 
    query += " ?ent1 <http://xmlns.com/foaf/0.1/name> ?nombre "
    query += " } "
    query += " group by ?urlID } "
    query += " union  { "
    query += "    select ?urlID   ?u ?t  ?nti"
    query += "    where { "
    query += "    ?urlID rdf:type schema:CreativeWork . "
    query += "    ?urlID rdf:type owl:NamedIndividual . "
    query += "    ?urlID schema:concept ?nti . "
    query += "    ?urlID schema:url  ?u  . "
    query += "    ?urlID schema:title ?t  "
    query +=" } } }"


    print(sparqlhelper.SparqlHelper.query_format(cfg.sparql_user,cfg.sparql_pass,cfg.sparql_server,cfg.sparql_path_auth,'?default-graph-uri=&should-sponge=&timeout=0&signal_void=on',query,"csv"))

def query3():

    query="PREFIX schema: <http://schema.org/> PREFIX nti: <http://datos.gob.es/kos/sector-publico/sector/>  PREFIX rdf:<http://www.w3.org/1999/02/22-rdf-syntax-ns#> PREFIX owl:<http://www.w3.org/2002/07/owl#> PREFIX ei2a:<http://opendata.aragon.es/def/ei2av2#> PREFIX locn: <http://www.w3.org/ns/locn#> PREFIX dc: <http://purl.org/dc/elements/1.1/title#>"
    query += "  SELECT ?urlID  group_concat(distinct ?u;separator='; ') as ?url  group_concat(distinct ?t;separator='; ') as ?t  group_concat(distinct ?nti;separator='; ') as ?nti WHERE { "
    query += " { "
    query += "    select ?urlID   ?u ?t  ?nti"
    query += "    where { "
    query += "    ?urlID rdf:type schema:CreativeWork . "
    query += "    ?urlID rdf:type owl:NamedIndividual . "
    query += "    ?urlID schema:concept ?nti . "
    query += "    ?urlID schema:url  ?u  . "
    query += "    ?urlID schema:title ?t  "
    query += "    } } }"

    print(sparqlhelper.SparqlHelper.query_format(cfg.sparql_user,cfg.sparql_pass,cfg.sparql_server,cfg.sparql_path_auth,'?default-graph-uri=&should-sponge=&timeout=0&signal_void=on',query,"csv"))

def query4():
    query="PREFIX schema: <http://schema.org/>   PREFIX rdf:<http://www.w3.org/1999/02/22-rdf-syntax-ns#> PREFIX owl:<http://www.w3.org/2002/07/owl#> PREFIX ei2a:<http://opendata.aragon.es/def/ei2av2#> PREFIX locn: <http://www.w3.org/ns/locn#> PREFIX dc: <http://purl.org/dc/elements/1.1/title#>"
    query += "  select * where { "
    query += "  SELECT ?urlID   group_concat(distinct ?u;separator='; ') as ?url  group_concat(distinct ?t;separator='; ') as ?t  group_concat(distinct ?nti;separator='; ') as ?nti   "
    query += " group_concat(distinct ?org ;separator='; ') as ?organizaciones  group_concat(distinct ?nombre ;separator='; ') as ?personas group_concat(distinct ?loc;separator='; ') as ?location  WHERE { " 
    query += " { "

    query += "    ?urlID rdf:type schema:CreativeWork . "
    query += "    ?urlID rdf:type owl:NamedIndividual . "
    query += "    ?urlID schema:concept ?nti . "
    query += "    ?urlID schema:url  ?u  . "
    query += "    ?urlID schema:title ?t  . "
    query += "   OPTIONAL{ ?urlID schema:about ?entLOC ."
    query += "    ?entLOC <http://www.w3.org/1999/02/22-rdf-syntax-ns#type>  <http://dbpedia.org/ontology/GovernmentalAdministrativeRegion> . "
    query += "    ?entLOC <http://www.w3.org/2000/01/rdf-schema#label> ?loc }"

    query += "   OPTIONAL { ?urlID schema:about ?entORG ."
    query += "    ?entORG <http://www.w3.org/1999/02/22-rdf-syntax-ns#type>   <http://www.w3.org/ns/org#Organization>. "
    query += "    ?entORG <http://purl.org/dc/elements/1.1/title> ?org }"

    query += " OPTIONAL{ ?urlID schema:about ?entNOM ."
    query += " ?entNOM <http://www.w3.org/1999/02/22-rdf-syntax-ns#type>  <http://xmlns.com/foaf/0.1/Person> . " 
    query += " ?entNOM <http://xmlns.com/foaf/0.1/name> ?nombre }"
    query +=" }  }"
    query += "    limit 10 } "
    # print(query)

    print(sparqlhelper.SparqlHelper.query_format(cfg.sparql_user,cfg.sparql_pass,cfg.sparql_server,cfg.sparql_path_auth,'?default-graph-uri=&should-sponge=&timeout=0&signal_void=on',query,'text/x-html tr'))


def query5():
    query="PREFIX schema: <http://schema.org/> PREFIX nti: <http://datos.gob.es/kos/sector-publico/sector/>  PREFIX rdf:<http://www.w3.org/1999/02/22-rdf-syntax-ns#> PREFIX owl:<http://www.w3.org/2002/07/owl#> PREFIX ei2a:<http://opendata.aragon.es/def/ei2av2#> PREFIX locn: <http://www.w3.org/ns/locn#> PREFIX dc: <http://purl.org/dc/elements/1.1/title#>"
    query += " select   COUNT(*)  AS ?count "
    query += "     where { "
    query += "    ?urlID rdf:type schema:CreativeWork . "
    query += "    ?urlID rdf:type owl:NamedIndividual . "
    query += "    ?urlID schema:concept ?nti . "
    query += "    ?urlID schema:url  ?u  . "
    query += "    } "   

    print(sparqlhelper.SparqlHelper.query_format(cfg.sparql_user,cfg.sparql_pass,cfg.sparql_server,cfg.sparql_path_auth,'?default-graph-uri=&should-sponge=&timeout=0&signal_void=on',query,"csv"))


def query6():
    query  = """
                    select ?s ?nombre  from <http://opendata.aragon.es/def/ei2av2> where  { 
                    ?s <http://www.w3.org/1999/02/22-rdf-syntax-ns#type>  <http://www.w3.org/ns/org#Organization>. 
                    ?s <http://purl.org/dc/elements/1.1/title> ?nombre  .
                    FILTER (?nombre ='NS') }
                    order by asc(?s) 
                """

    print(sparqlhelper.SparqlHelper.query_format(cfg.sparql_user,cfg.sparql_pass,cfg.sparql_server,cfg.sparql_path_auth,cfg.querystring,query,"csv"))



def test7():
    query  = """
                    select ?s ?nombre  from <http://opendata.aragon.es/def/ei2av2> where  { 
                    ?s <http://www.w3.org/1999/02/22-rdf-syntax-ns#type>  <http://www.w3.org/ns/org#Organization>. 
                    ?s <http://purl.org/dc/elements/1.1/title> ?nombre  }                   
                    order by asc(?s) 
                """
    sparqlhelper.SparqlHelper.queryPaged(cfg.sparql_user,cfg.sparql_pass,cfg.sparql_server,cfg.sparql_path_auth,cfg.querystring,query,1,True)



def deleteall():
    query="PREFIX schema: <http://schema.org/> PREFIX nti: <http://datos.gob.es/kos/sector-publico/sector/>  PREFIX rdf:<http://www.w3.org/1999/02/22-rdf-syntax-ns#> PREFIX owl:<http://www.w3.org/2002/07/owl#> PREFIX ei2a:<http://opendata.aragon.es/def/ei2av2#> PREFIX locn: <http://www.w3.org/ns/locn#> PREFIX dc: <http://purl.org/dc/elements/1.1/title#>"
    query += "  select * where { "
    query += "   select ?urlID  "
    query += "     where { "
    query += "    ?urlID rdf:type schema:CreativeWork . "
    query += "    ?urlID rdf:type owl:NamedIndividual . "
    query += "    ?urlID schema:concept ?nti . "
    query += "    ?urlID schema:url  ?u  . "

    query += "    } "
    query += "    limit 5000 } "

    resultados=str(sparqlhelper.SparqlHelper.query_format(cfg.sparql_user,cfg.sparql_pass,cfg.sparql_server,cfg.sparql_path_auth,'?default-graph-uri=&should-sponge=&timeout=0&signal_void=on',query,"csv"))
    reader = csv.reader(resultados.split("\\n"))
    next(reader)
    for row in reader:
        for col in row:
            print("  ", col)
            querydelete =" DELETE WHERE { GRAPH <http://opendata.aragon.es/def/ei2av2> {<" + col +"> ?x ?y } }"
            sparqlhelper.SparqlHelper.query(cfg.sparql_user,cfg.sparql_pass,cfg.sparql_server,cfg.sparql_path_auth,cfg.querystring,querydelete)     
      

query4()
deleteall()
query4()