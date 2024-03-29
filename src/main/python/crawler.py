import logging
from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import csv
import sparqlhelper
import base64
from summa.summarizer import summarize
import fitz
import zlib
import config as cfg
import os.path
import re
from datetime import datetime
import time





logging.basicConfig(
    format='%(asctime)s %(levelname)s:%(message)s',
    level=logging.INFO)

class Crawler:
     

   
    
    def __init__(self):
        self.starttime = time.time()
        self.visited_urls = []
        self.urls_to_visit = []
        self.no_visit_default = cfg.no_visit
        self.no_visit = []
        self.sectoresMap={}
        self.sparqlHelper=sparqlhelper.SparqlHelper
        self.sparql_user=cfg.sparql_user
        self.sparql_pass=cfg.sparql_pass
        self.sparql_server=cfg.sparql_server
        self.sparql_path=cfg.sparql_path
        self.sparql_path_auth=cfg.sparql_path_auth
        self.querystring=cfg.querystring
        self.processed=0
        self.added=0
        self.maps=[]
        self.load_urls(cfg.urlsfile)
        self.depth= cfg.depth 
        self.loadData()

    def load_urls(self,urlsfile):
        if os.path.exists(urlsfile) :
            with open(urlsfile, mode='r') as infile:   
                reader = csv.reader(infile)
                next(reader)
                for row in reader:
                    url=row[0]
                    self.sectoresMap[url]=row[1]                 
        else:
            self.sectoresMap=cfg.urls

        for url in self.sectoresMap:
            self.urls_to_visit.append(url)

    def loadData(self):    
   

        query1  = """
                    select ?s ?nombre  from <http://opendata.aragon.es/def/ei2av2> where  { 
                    ?s <http://www.w3.org/1999/02/22-rdf-syntax-ns#type>  <http://www.w3.org/ns/org#Organization>. 
                    ?s <http://purl.org/dc/elements/1.1/title> ?nombre  }
                    order by asc(?s) 
                """
        query2 =  """ 
            select ?s ?nombre from <http://opendata.aragon.es/def/ei2av2>  
            where  {
            ?s <http://www.w3.org/1999/02/22-rdf-syntax-ns#type>  <http://xmlns.com/foaf/0.1/Person>. 
            ?s <http://xmlns.com/foaf/0.1/name> ?nombre  } 
            order by asc(?s) 
            """

        query3 = """ 
            select ?s ?nombre from <http://opendata.aragon.es/def/ei2av2> 
            where  { 
            ?s <http://www.w3.org/1999/02/22-rdf-syntax-ns#type>  <http://www.w3.org/ns/org#Role> .
            ?s <http://purl.org/dc/elements/1.1/title> ?nombre  }
            order by asc(?s) 
            """

        query4 = """
            select ?s  ?nombre  
            where  {
            ?s <http://www.w3.org/1999/02/22-rdf-syntax-ns#type>  <http://dbpedia.org/ontology/GovernmentalAdministrativeRegion> . 
            ?s <http://www.w3.org/2000/01/rdf-schema#label> ?nombre  }
            order by asc(?s) 
            """
      
        self.maps.append(self.sparqlHelper.queryPaged(self.sparql_user,self.sparql_pass,self.sparql_server,self.sparql_path_auth,self.querystring,query1,1,True,True))
        self.maps.append(self.sparqlHelper.queryPaged(self.sparql_user,self.sparql_pass,self.sparql_server,self.sparql_path_auth,self.querystring,query2,2,True,False))
        self.maps.append(self.sparqlHelper.queryPaged(self.sparql_user,self.sparql_pass,self.sparql_server,self.sparql_path_auth,self.querystring,query3,2,True,False))
        self.maps.append(self.sparqlHelper.queryPaged(self.sparql_user,self.sparql_pass,self.sparql_server,self.sparql_path_auth,self.querystring,query4,1,True,False))

        #self.maps.append(self.sparqlHelper.queryGet( self.sparql_server,self.sparql_path+self.querystring,query1,1))
        #self.maps.append(self.sparqlHelper.queryGet(self.sparql_server,self.sparql_path+self.querystring,query2,2))
        #self.maps.append(self.sparqlHelper.queryGet(self.sparql_server,self.sparql_path+self.querystring,query3,2))
        #self.maps.append(self.sparqlHelper.queryGet(self.sparql_server,self.sparql_path+self.querystring,query4,1))

        
        
       

    def get_linked_urls(self, url, soup):
       
        for link in soup.find_all('a'):
            path = link.get('href')
            if path and path.startswith('/') and url.startswith('http') :
                path = urljoin(url, path)
            yield path

    def add_url_to_visit(self, url):
        
        if url is not None :
            
            if ";jsessionid=" in url:
                url=url[:url.index(";jsessionid=")-1]             
            # la longitud de la url no puede ser mayor de 299 caracteres ni menor de 6
            if url not in self.visited_urls and url not in self.urls_to_visit and url not in self.no_visit and self.check_no_visit_def(url) and len(url)<300 and len(url)>10 :
                url_dept=url[10:].count('/')
                if  url_dept<self.depth and not url.endswith(('.csv','.xls','.xlsx','.jpg','.png','.gif','.css','.xml','.mp3','.mp4')):
                    self.urls_to_visit.append(url)
                else: 
                    self.no_visit.append(url)



    def check_no_visit_def(self,url):
        for nv in self.no_visit_default:
            if nv in url:
                return False 
        return True


    def _remove_divs(self,soup,attrs,values):
        for attribute in attrs:
            for v in values:
                for div in soup.findAll(attrs={attribute : v }):
                    #print(div)
                    div.decompose()
                #if tag in tags:
                #    del tag[attribute]
    def keepParagraphTags(self,soup,tags):
        for para in soup.find_all("p"): 
            children = para.getAllElements()
            for f  in children[1:] :
                remove = True
                for tag  in tags:
                    if f.tagName().equals(tag):
                        remove = False
                        break                    
                if (remove):
                    f.remove()
  

    def cleanHtml(self,  soup):
            
        tit = soup.find('title')
      
        title=""
        if tit is not None:
            title= tit.string
            tit.decompose()

        tags = ["footer", "header", "nav", "form","style", "meta","script"]
        for tag in tags:
            for div in soup.find_all(tag): 
                #reset
                #  print(div)
                div.decompose()

      
        attrs = ["class", "id"]
        tags = ["footer", "Footer", "nav", "Nav", "banner", "Banner", "box", "Box", "pie", "Pie","rightBlock","menu","block-menu"]
        self._remove_divs(soup,attrs,tags)
       
        for x in soup.find_all("p"):
            text=x.get_text()
            if len(text.split(" ")) <5 or "cookies" in text:
                # Remove tag
                x.decompose()         
     
        texto =  '. '.join(soup.stripped_strings)
        texto=texto.replace("..",".")        
     
        return title,texto

        
    def build_uri_id(self,url ):
       #usamos este diccionario para acortar la longitud de la url codigficada
        diccionario={ "https://transparencia.aragon.es":"11",
                      "https://www.saludinforma.es":"12",
                      "https://educa.aragon.es":"13",
                      "https://www.turismodearagon.com":"14",
                      "https://acpua.aragon.es":"15",
                      "https://www.aragon.es":"16",
                      "http://www.aragonhoy.net":"17"}
        prefix="99"
        sectorTemp="sector-publico"
           
        if self.sectoresMap is not None:
            for key in self.sectoresMap:
                if url.startswith(key):
                    sectorTemp = self.sectoresMap[key]
                    break                
           
        pathInputString=url
   
        for key in  diccionario:
            if url.startswith(key):
                pathInputString = url[len(key):]
                prefix = diccionario[key]
                 
        uriTemp=prefix+base64.urlsafe_b64encode(pathInputString.encode('utf-8')).decode('utf-8').replace("=","")        
        return uriTemp,sectorTemp

    def summarize_text(self,html):
        summary_text=""
        if len(html) == 0:
            message = 'No hay texto disponible para realizar el resumen.'
        else:     
            message = 'El resumen se ha realizado satisfactoriamente.'
            summary_text  = summarize(html, 
                                      ratio=0.2, 
                                      words=None, 
                                      language='spanish', 
                                      split=False, 
                                      scores=False, 
                                      additional_stopwords=None)  

      
        return summary_text.replace("'"," ")
         

    def pdf_to_text(self,content):
        all_Pages=""
        doc = fitz.open(stream=content, filetype="pdf")
        title=doc.metadata["title"]
        for page in doc:   
            all_Pages += page.get_text()
        return title,all_Pages


    def check_webpage_changes(self,newcrc,sector,uriID):
      
        oldcrc=0
        hasChanged=True
        try:
            query = "PREFIX schema: <http://schema.org/>  PREFIX recurso: <http://opendata.aragon.es/recurso/"+sector+"/documento/webpage/>  select ?crc  from <http://opendata.aragon.es/def/ei2av2> where  {  recurso:"+uriID+" schema:version   ?crc}"

            data=self.sparqlHelper.query(self.sparql_user,self.sparql_pass,self.sparql_server,self.sparql_path_auth,self.querystring,query)
        
            lines=data["results"]["bindings"]
           
            if lines is not None and len(lines)>0:
                oldcrc=lines[0]["crc"]["value"]  

            if oldcrc==str(newcrc):
                hasChanged=False
        except:
            hasChanged=True
        return hasChanged

    def delete_old_values(self,sector,uriID):
        
        query ="PREFIX recurso: <http://opendata.aragon.es/recurso/"+sector+"/documento/webpage/> DELETE WHERE { GRAPH <http://opendata.aragon.es/def/ei2av2> {recurso:" + uriID +" ?x ?y } }"

        self.sparqlHelper.query(self.sparql_user,self.sparql_pass,self.sparql_server,self.sparql_path_auth,self.querystring,query)           
          

    def insert_data(self,uriID,sector,url,crc,title,summary,texto):
        
        query = f"PREFIX schema: <http://schema.org/>   PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> "
        query = f"{query} PREFIX owl: <http://www.w3.org/2002/07/owl#>  PREFIX recurso: <http://opendata.aragon.es/recurso/{sector}/documento/webpage/> "        
        query = f"{query} PREFIX nti: <http://datos.gob.es/kos/sector-publico/sector/> "
        query = f"{query} INSERT DATA {{ GRAPH <http://opendata.aragon.es/def/ei2av2> {{ "
        query = f"{query}  recurso:{uriID} rdf:type schema:CreativeWork . "
        query = f"{query}  recurso:{uriID} rdf:type owl:NamedIndividual  . "
        query = f"{query}  recurso:{uriID} schema:url  '{url}'  . "
        query = f"{query}  recurso:{uriID} schema:title '{title}'  ."
        query = f"{query}  recurso:{uriID} schema:version '{str(crc)}' . "
        query = f"{query}  recurso:{uriID} schema:abstract '{summary}' . "
        query = f"{query}  recurso:{uriID} schema:concept nti:{sector} . "
        query = f"{query}  recurso:{uriID} schema:sdDatePublished   '{ datetime.now().strftime('%Y%m%d')}' "

        try:
          
            textosinacentos=sparqlhelper.eliminar_acentos(texto)
            textosinespaciosmultiples=str(re.sub(' +', ' ',textosinacentos))
            addedIds=set()
            for map in self.maps:
                for key in map :
                    if key in textosinespaciosmultiples:
                        #pattern=r'[\.+|\s+|^|-]('+key+r')[\s|\.|$|-]*'
                        pattern=r'\b'+key+r'\b'
                        match=re.search(pattern,textosinespaciosmultiples.replace("."," ")) 
                        if match is not None:
                            if map[key] not in  addedIds:
                                # no incluir duplicados de uris iguales que puedan tener distinto nombre
                                addedIds.add(map[key])
                                query = f"{query} . recurso:{uriID} schema:about <{map[key]}> "
        except:
            pass

        query = f"{query} }} }}"
        #print(query)
        return(self.sparqlHelper.insertdata(self.sparql_user,self.sparql_pass,self.sparql_server,self.sparql_path_auth,self.querystring,query))


  

    def crawl(self, url):

        #descargamos el contenido de la url, puede ser una web o un pdf  
        response=requests.get(url)
        if response.status_code == 200:
            headers = response.headers
            uriID,sector=self.build_uri_id(url)
            contentType = str(headers['content-type'])
            hasChanged=True
            new_crc=0
            titulo=""
            texto=""
            domain = urlparse(url).netloc
            domain=domain.replace("www.","")      
            raw_text=""
            if "text" in contentType: # aunque se descartan ciertas extensiones pueden venir datos en formatos no deseados
                raw_text =  response.text
                #calcula el crc para ver si ha cambiado lo que hay en la bd
              
                soup = BeautifulSoup(raw_text, 'html.parser')
                titulo,texto=self.cleanHtml(soup)
                new_crc=zlib.crc32(texto.encode('utf-8'))
                #si no es pdf busca los enlaces y los añadimos a la lista de url a procesar
                for urlTemp in self.get_linked_urls(url, soup):
                    try:
                        if urlTemp is not None and  domain in urlTemp: 
                            domainTemp = urlparse(urlTemp).netloc
                            domainTemp=domainTemp.replace("www.","")    
                            if  domain==domainTemp:
                                self.add_url_to_visit(urlTemp)
                    except:
                        pass
            elif  "pdf"  in contentType:
            #calcula el crc para ver si ha cambiado lo que hay en la bd
                try:
                    contentLength = str(headers['content-length'])	          
                    if  int(str(contentLength)) < 1024*1024:  #solo procesamos los pdf menores de 1MB
                        new_crc=zlib.crc32(response.content)
                    else:
                        logging.info("Archivo pdf descartado")
                        return
                except:
                    return
            else:          
                return
            #comprueba en la bd si ha habido cambios
            # si no existe se devuelve true 
            hasChanged=self.check_webpage_changes(new_crc,sector,uriID)          
            #logging.info("Inserting :"+ str(hasChanged)) 

            self.processed= self.processed+1     
      
            if hasChanged:
                 #print(contentType)
                #extrae el contenido
                if "pdf"  in contentType:
                    titulo,texto=self.pdf_to_text(response.content) 
            
                #resume el contenido
                summary=self.summarize_text(texto)  
                summary=summary.replace("\n"," ") 
                summary=re.sub(' +', ' ',summary) #eliminamos los espacios multiples
                #borra los datos antiguos
                self.delete_old_values(sector,uriID)
                # inserta los nuevos datos  
                logging.info(self.insert_data(uriID,sector,url,new_crc,titulo,summary,texto) )
                self.added=self.added+1

    def run(self):
        while self.urls_to_visit:
            url = self.urls_to_visit.pop(0)
            try:
                logging.info(f'Crawling: {url}')
                                   
                self.crawl(url)
                logging.info(f'pending url: {len(self.urls_to_visit)}')
            except Exception:
                logging.info(f'EXCEPTION  Failed to crawl: {url}')
                logging.exception(f'Failed to crawl: {url}')
            finally:
                self.visited_urls.append(url)
        self.endtime = time.time()
        logging.info(f'SUMMARY:  processed: {self.processed}  added:{self.added}')
        logging.info(f'TIME:  { str(self.endtime- self.starttime)} seconds')
       
if __name__ == '__main__':
    crawler=Crawler().run()
  
    #crawler.crawl("http://www.patrimonioculturaldearagon.es/agenda-portada/primera-temporada-de-lirica-y-danza-2021")
   
