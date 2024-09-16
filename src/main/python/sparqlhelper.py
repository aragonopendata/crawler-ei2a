import json
import requests
import logging
from requests.auth import HTTPDigestAuth
import urllib
import re


logging.basicConfig(
    format='%(asctime)s %(levelname)s:%(message)s',
    level=logging.INFO)



class SparqlHelper():


    def insertdata(sparql_user,sparql_pass,sparql_server,sparql_path_auth,querystring,query):

        url = sparql_server+sparql_path_auth+querystring
    
        #print(query)
        headers={}
        headers["Content-Type"]="application/sparql-query"
        data=query.encode('utf-8')
        resp = requests.post(url, headers=headers,auth=HTTPDigestAuth(sparql_user,sparql_pass ),  data=data,   timeout=10)

       
        if resp.status_code!=200:
            logging.info(resp.content)
        return resp.status_code
    
    def query(sparql_user,sparql_pass,sparql_server,sparql_path_auth,querystring,query):

        url = sparql_server+sparql_path_auth+querystring+"&format=format=application/json"
    
        headers={}
        headers["Content-Type"]="application/sparql-query"

        resp = requests.post(url, headers=headers,auth=HTTPDigestAuth(sparql_user,sparql_pass ),  data=query,   timeout=10)

        data= json.loads(resp.content)  

        return data

  
    def query_format(sparql_user,sparql_pass,sparql_server,sparql_path_auth,querystring,query,format):

        url = sparql_server+sparql_path_auth+querystring+"&format="+format
    
        headers={}
        headers["Content-Type"]="application/sparql-query"

        resp = requests.post(url, headers=headers,auth=HTTPDigestAuth(sparql_user,sparql_pass ),  data=query,   timeout=10)

       
        return resp.content   

    def query_paged(sparql_user,sparql_pass,sparql_server,sparql_path_auth,querystring,query,min_words=1,title=False,parentesis=False):

        url = sparql_server+sparql_path_auth+querystring+"&format=format=application/json"
    
        headers={}
        headers["Content-Type"]="application/sparql-query"
        offset=0
        limit=10000
        query_offset=""
        map_temp={}
        try:
            while True:
            
                query_offset= "select * where { " + query +" }  offset "+ str(offset) + " limit " +str(limit) 
                resp = requests.post(url, headers=headers,auth=HTTPDigestAuth(sparql_user,sparql_pass ),  data=query_offset,   timeout=10)

                data= json.loads(resp.content)  
                lines=data["results"]["bindings"]
                offset = offset+limit
                                    
                map_temp={}
                for  line  in  lines :
                    uri=line["s"]["value"]
                    nombre=line["nombre"]["value"]
                    words=nombre.split(" ")
                    if len(words)>=min_words:
                        try:
                            n=str(nombre).replace("\"","")
                            n=re.sub(' +', ' ',n) #eliminamos los espacios multiples
                            n=eliminar_acentos(n).strip()
                            n=n.replace("Arag?n","Aragon")
                            
                            if n.endswith((' (La)',' (Las)',' (El)',' (Los)',' (LAS)',' (LA)',' (EL)',' (LOS)')):
                                n=n[n.rfind(" ")+2:len(n)-1].title()+ " " +n[:n.rfind(" ")]
                            if title:
                                n=n.title()
                                n=n.replace(" El "," el ").replace(" La "," la ").replace(" Los "," los ").replace(" Las "," las ").replace(" Del "," del ").replace(" De "," de ").replace(" Y "," y ").replace(" Un "," un ").replace(" Una "," una ").replace(" En "," en ").replace(" E "," e ")
                                n=n.replace(" Ii"," II").replace(" Iii"," III").replace(" Iv "," IV ").replace(" Vi "," VI ").replace(" Vii"," VII").replace(" Viii"," VIII").replace(" Ix "," IX ")
                            
                            grupo=re.search('\(([^)]+)', n)
                            uri=uri.replace("\"","").strip()
                            if (grupo is not None):  
                                grupo1=grupo.group(1)
                                if parentesis:
                                    map_temp[grupo1.strip()]=uri
                                    map_temp[grupo1.upper().strip()]=uri
                                keyy=n[:grupo.start()].strip()
                                map_temp[keyy]=uri
                            else:
                                map_temp[n]=uri
                            
                        except Exception as inst:
                            print(inst)    # the exception instance
                            pass
                if len(lines)<limit:
                    break
        except:            
            pass
        return map_temp
   
    def query_get(sparql_server,sparql_path,query,min_words=1,title=False):

        url = sparql_server+sparql_path    
       
        offset=0
        limit=10000
        query_offset=""
        map_temp={}
        try:
            while True:
            
                query_offset= "select * where { " + query +" }  offset "+ str(offset) + " limit " +str(limit) 
                resp = requests.get(url+"&query="+urllib.parse.quote_plus(query_offset), timeout=10)
            
                data= json.loads(resp.content)  
                lines=data["results"]["bindings"]
                print(len(lines))
                offset = offset+limit
                                    
                map_temp={}
                for  line  in  lines :
                    uri=line["s"]["value"]

                    nombre=line["nombre"]["value"]
                    n=str(nombre)        
                    words=nombre.split(" ")
                    if len(words)>=min_words:
                        try:
                            n=nombre.replace("\"","")
                            n=eliminar_acentos(n)
                            n=re.sub(' +', ' ',n) #eliminamos los espacios multiples
                            n=n.replace(" ","").replace("(la)","").replace("(La)","").replace("(las)","").replace("(Las)","").replace("(los)","").replace("(Los)","").replace("(el)","").replace("(El)","").replace("Arag?n","aragon")
                            if (title):
                                n=n.title()
                                n=n.replace(" El "," el ").replace(" La "," la ").replace(" del "," del ").replace(" de "," de ").replace(" Y "," y ").replace(" Un "," un ").replace(" Una "," una ")
                            map_temp[n]=uri.replace("\"","")
                        except Exception as inst:
                            logging.exception(f"Unexpected error in query_get function: {inst}")
                if len(lines)<limit:
                    break
        except Exception as e:
            logging.exception(f"Unexpected error in query_get function: {e}")
        return map_temp

def eliminar_acentos(texto):
    textosinacentos=texto.replace( "á","a").replace("é","e").replace("í","i").replace("ó","o").replace("ú","u").replace("ü","u")
    textosinacentos=textosinacentos.replace( "Á","A").replace("É","E").replace("Í","I").replace("Ó","o").replace("Ú","U").replace("Ü","U")
    return textosinacentos