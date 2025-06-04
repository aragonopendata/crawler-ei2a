import json
import requests
import logging
from requests.auth import HTTPDigestAuth
import urllib
import re
import time

logging.basicConfig(
    format='%(asctime)s %(levelname)s:%(message)s',
    level=logging.INFO)

class SparqlHelper():

    @staticmethod
    def insertdata(sparql_user, sparql_pass, sparql_server, sparql_path_auth, querystring, query, max_retries=3):
        """
        Inserta datos con reintentos automáticos
        """
        url = sparql_server + sparql_path_auth + querystring
        headers = {"Content-Type": "application/sparql-query"}
        data = query.encode('utf-8')
        
        for attempt in range(max_retries):
            try:
                resp = requests.post(url, headers=headers, auth=HTTPDigestAuth(sparql_user, sparql_pass), 
                                   data=data, timeout=30)
                
                if resp.status_code == 200:
                    return resp.status_code
                elif resp.status_code == 404:
                    logging.warning(f"Endpoint not found (404). Attempt {attempt + 1}/{max_retries}")
                    if attempt < max_retries - 1:
                        time.sleep(2 ** attempt)  # Backoff exponencial
                        continue
                else:
                    logging.error(f"SPARQL Insert failed with status {resp.status_code}: {resp.content}")
                    
                return resp.status_code
                
            except requests.exceptions.Timeout:
                logging.error(f"SPARQL Insert timeout. Attempt {attempt + 1}/{max_retries}")
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)
                    continue
                return 408
            except requests.exceptions.ConnectionError as e:
                logging.error(f"SPARQL Insert connection error. Attempt {attempt + 1}/{max_retries}: {e}")
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)
                    continue
                return 500
            except requests.exceptions.RequestException as e:
                logging.error(f"SPARQL Insert request error: {e}")
                return 500
        
        return 500  # Si llegamos aquí, todos los reintentos fallaron
    
    @staticmethod
    def query(sparql_user, sparql_pass, sparql_server, sparql_path_auth, querystring, query, max_retries=3):
        """
        Ejecuta consulta con reintentos automáticos
        """
        url = sparql_server + sparql_path_auth + querystring + "&format=application/json"
        headers = {"Content-Type": "application/sparql-query"}

        for attempt in range(max_retries):
            try:
                resp = requests.post(url, headers=headers, auth=HTTPDigestAuth(sparql_user, sparql_pass), 
                                   data=query, timeout=30)
                
                if resp.status_code == 200:
                    # Verificar que el content-type sea JSON
                    content_type = resp.headers.get('content-type', '').lower()
                    if 'application/json' not in content_type:
                        logging.error(f"SPARQL Query returned non-JSON content-type: {content_type}")
                        return {"results": {"bindings": []}}
                    
                    # Verificar que el contenido no esté vacío
                    if not resp.content.strip():
                        logging.error("SPARQL Query returned empty response")
                        return {"results": {"bindings": []}}
                        
                    try:
                        data = json.loads(resp.content)
                        return data
                    except json.JSONDecodeError as e:
                        logging.error(f"SPARQL Query JSON decode error: {e}")
                        return {"results": {"bindings": []}}
                        
                elif resp.status_code == 404:
                    logging.warning(f"Endpoint not found (404). Attempt {attempt + 1}/{max_retries}")
                    if attempt < max_retries - 1:
                        time.sleep(2 ** attempt)
                        continue
                else:
                    logging.error(f"SPARQL Query failed with status {resp.status_code}: {resp.content}")
                    return {"results": {"bindings": []}}
                    
            except requests.exceptions.Timeout:
                logging.error(f"SPARQL Query timeout. Attempt {attempt + 1}/{max_retries}")
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)
                    continue
            except requests.exceptions.ConnectionError as e:
                logging.error(f"SPARQL Query connection error. Attempt {attempt + 1}/{max_retries}: {e}")
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)
                    continue
            except requests.exceptions.RequestException as e:
                logging.error(f"SPARQL Query request error: {e}")
                break
        
        return {"results": {"bindings": []}}

    @staticmethod
    def query_format(sparql_user, sparql_pass, sparql_server, sparql_path_auth, querystring, query, format):
        url = sparql_server + sparql_path_auth + querystring + "&format=" + format
        
        headers = {}
        headers["Content-Type"] = "application/sparql-query"

        try:
            resp = requests.post(url, headers=headers, auth=HTTPDigestAuth(sparql_user, sparql_pass), 
                               data=query, timeout=30)
            return resp.content
        except requests.exceptions.RequestException as e:
            logging.error(f"SPARQL Query format error: {e}")
            return b""

    @staticmethod
    def query_paged(sparql_user, sparql_pass, sparql_server, sparql_path_auth, querystring, query, 
                   min_words=1, title=False, parentesis=False):
        url = sparql_server + sparql_path_auth + querystring + "&format=application/json"
        
        headers = {}
        headers["Content-Type"] = "application/sparql-query"
        offset = 0
        limit = 10000
        map_temp = {}
        
        try:
            while True:
                query_offset = "select * where { " + query + " } offset " + str(offset) + " limit " + str(limit)
                
                try:
                    resp = requests.post(url, headers=headers, auth=HTTPDigestAuth(sparql_user, sparql_pass), 
                                       data=query_offset, timeout=30)
                    
                    if resp.status_code != 200:
                        logging.error(f"SPARQL Paged query failed with status {resp.status_code}")
                        break
                        
                    if not resp.content.strip():
                        logging.error("SPARQL Paged query returned empty response")
                        break
                        
                    data = json.loads(resp.content)
                    lines = data["results"]["bindings"]
                    offset = offset + limit
                    
                    for line in lines:
                        uri = line["s"]["value"]
                        nombre = line["nombre"]["value"]
                        words = nombre.split(" ")
                        if len(words) >= min_words:
                            try:
                                n = str(nombre).replace("\"", "")
                                n = re.sub(' +', ' ', n)  # eliminamos los espacios multiples
                                n = eliminar_acentos(n).strip()
                                n = n.replace("Arag?n", "Aragon")
                                
                                if n.endswith((' (La)', ' (Las)', ' (El)', ' (Los)', ' (LAS)', ' (LA)', ' (EL)', ' (LOS)')):
                                    n = n[n.rfind(" ")+2:len(n)-1].title() + " " + n[:n.rfind(" ")]
                                if title:
                                    n = n.title()
                                    n = n.replace(" El ", " el ").replace(" La ", " la ").replace(" Los ", " los ").replace(" Las ", " las ").replace(" Del ", " del ").replace(" De ", " de ").replace(" Y ", " y ").replace(" Un ", " un ").replace(" Una ", " una ").replace(" En ", " en ").replace(" E ", " e ")
                                    n = n.replace(" Ii", " II").replace(" Iii", " III").replace(" Iv ", " IV ").replace(" Vi ", " VI ").replace(" Vii", " VII").replace(" Viii", " VIII").replace(" Ix ", " IX ")
                                
                                grupo = re.search('\(([^)]+)', n)
                                uri = uri.replace("\"", "").strip()
                                if (grupo is not None):
                                    grupo1 = grupo.group(1)
                                    if parentesis:
                                        map_temp[grupo1.strip()] = uri
                                        map_temp[grupo1.upper().strip()] = uri
                                    keyy = n[:grupo.start()].strip()
                                    map_temp[keyy] = uri
                                else:
                                    map_temp[n] = uri
                                    
                            except Exception as inst:
                                logging.error(f"Error processing line: {inst}")
                                pass
                                
                    if len(lines) < limit:
                        break
                        
                except json.JSONDecodeError as e:
                    logging.error(f"SPARQL Paged query JSON decode error: {e}")
                    break
                except requests.exceptions.RequestException as e:
                    logging.error(f"SPARQL Paged query request error: {e}")
                    break
                    
        except Exception as e:
            logging.error(f"SPARQL Paged query unexpected error: {e}")
            
        return map_temp

def eliminar_acentos(texto):
    textosinacentos = texto.replace("á", "a").replace("é", "e").replace("í", "i").replace("ó", "o").replace("ú", "u").replace("ü", "u")
    textosinacentos = textosinacentos.replace("Á", "A").replace("É", "E").replace("Í", "I").replace("Ó", "o").replace("Ú", "U").replace("Ü", "U")
    return textosinacentos