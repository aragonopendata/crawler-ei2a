import pysolr

SOLR_URL = "http://argon-solr:8975/solr/opendata"
solr = pysolr.Solr(SOLR_URL, timeout=10)

def delete_all():
    solr.delete(q='*:*')

def show_all():
    query = solr.search(q='*:*', rows=100000)
    for q in query:
        print("-----")
        for key in q:
            print(key)

    print(len(query))

def insert(doc):
    try:
        solr.add([doc])
    except pysolr.SolrError:
        print("Error: Cannot insert in Solr")

# Make a query to a Solr data base if the node represents a web page
def get_info_solr(url):
    query =  'url:"' + url + '"'
    data = solr.search(q=query,fl='texto,categorias,personas,organizaciones,localizaciones,actualDate')
    results = list(data)
    if results:
        doc = results[0]
        doc["categorias"] = [categoria.split("#")[1] for categoria in doc["categorias"] ]
        return doc
