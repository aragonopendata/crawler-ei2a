import base64
import csv
import logging
import os.path
import re
import time
import zlib
from datetime import datetime
from urllib.parse import urljoin
from urllib.parse import urlparse

import fitz
import requests
from bs4 import BeautifulSoup
from summa.summarizer import summarize
from dotenv import load_dotenv

import config as cfg
import sparqlhelper

from opentelemetry_config import OpenTelemetryConfig
from opentelemetry.trace import get_current_span
from opentelemetry.trace.status import Status, StatusCode
from opentelemetry import trace
from opentelemetry.trace import Status, StatusCode

load_dotenv()
logging.basicConfig(
    format='%(asctime)s %(levelname)s:%(message)s',
    level=logging.ERROR
)


class Crawler:

    def __init__(self):
        self.starttime = time.time()
        self.endtime = None
        self.visited_urls = []
        self.urls_to_visit = []
        self.no_visit_default = cfg.no_visit
        self.no_visit = []
        self.sectores_map = {}
        self.sparql_helper = sparqlhelper.SparqlHelper
        self.sparql_user = os.getenv('SPARQL_USER')
        self.sparql_pass = os.getenv('SPARQL_PASS')
        self.sparql_server = os.getenv('SPARQL_SERVER')
        self.jaeger_endpoint = os.getenv('JAEGER_ENDPOINT')
        self.apm_endpoint = os.getenv('APM_ENDPOINT')
        self.sparql_path = cfg.sparql_path
        self.sparql_path_auth = cfg.sparql_path_auth
        self.querystring = cfg.querystring
        self.processed = 0
        self.added = 0
        self.maps = []

        OpenTelemetryConfig.initialize(
            service_name="CrawlerService",
            otlp_endpoint=self.apm_endpoint
        )
        self.tracer = OpenTelemetryConfig.get_tracer()

        self.load_urls(cfg.urlsfile)
        self.depth = cfg.depth
        self.load_data()

    def load_urls(self, urlsfile):

        try:

            if os.path.exists(urlsfile):
                with open(urlsfile, mode='r') as infile:
                    reader = csv.reader(infile)
                    next(reader)
                    for row in reader:
                        url = row[0]
                        self.sectores_map[url] = row[1]
            else:
                self.sectores_map = cfg.urls

            for url in self.sectores_map:
                self.urls_to_visit.append(url)

        except Exception as e:
            logging.exception("Error loading URLs")

    def load_data(self):

        query1 = """
                    select ?s ?nombre  from <http://opendata.aragon.es/def/ei2av2> where  { 
                    ?s <http://www.w3.org/1999/02/22-rdf-syntax-ns#type>  <http://www.w3.org/ns/org#Organization>. 
                    ?s <http://purl.org/dc/elements/1.1/title> ?nombre  }
                    order by asc(?s) 
                """
        query2 = """ 
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

        self.maps.append(
            self.sparql_helper.query_paged(self.sparql_user, self.sparql_pass, self.sparql_server, self.sparql_path_auth,
                                         self.querystring, query1, 1, True, True))
        self.maps.append(
            self.sparql_helper.query_paged(self.sparql_user, self.sparql_pass, self.sparql_server, self.sparql_path_auth,
                                         self.querystring, query2, 2, True, False))
        self.maps.append(
            self.sparql_helper.query_paged(self.sparql_user, self.sparql_pass, self.sparql_server, self.sparql_path_auth,
                                         self.querystring, query3, 2, True, False))
        self.maps.append(
            self.sparql_helper.query_paged(self.sparql_user, self.sparql_pass, self.sparql_server, self.sparql_path_auth,
                                         self.querystring, query4, 1, True, False))

        # self.maps.append(self.sparql_helper.query_get( self.sparql_server,self.sparql_path+self.querystring,query1,1))
        # self.maps.append(self.sparql_helper.query_get(self.sparql_server,self.sparql_path+self.querystring,query2,2))
        # self.maps.append(self.sparql_helper.query_get(self.sparql_server,self.sparql_path+self.querystring,query3,2))
        # self.maps.append(self.sparql_helper.query_get(self.sparql_server,self.sparql_path+self.querystring,query4,1))

    #@staticmethod
    def get_linked_urls(self, url, soup):
        start_time = time.time()
        try:
            total_links = 0
            linked_urls = []

            for link in soup.find_all('a'):
                path = link.get('href')
                if path and path.startswith('/') and url.startswith('http'):
                    path = urljoin(url, path)
                    total_links += 1
                    linked_urls.append(path)
                yield path

        except Exception as e:
            logging.exception("Error during linked URL extraction")
        finally:
            elapsed = time.time() - start_time
            self.link_extraction_time.record(elapsed)

    def add_url_to_visit(self, url):
        if url is not None:
            if ";jsessionid=" in url:
                url = url[:url.index(";jsessionid=") - 1]
            if url not in self.visited_urls and url not in self.urls_to_visit and url not in self.no_visit and self.check_no_visit_def(
                    url) and len(url) < 300 and len(url) > 10:
                url_dept = url[10:].count('/')
                if url_dept < self.depth and not url.endswith(
                        ('.csv', '.xls', '.xlsx', '.jpg', '.png', '.gif', '.css', '.xml', '.mp3', '.mp4')):
                    self.urls_to_visit.append(url)
                else:
                    self.no_visit.append(url)


    def check_no_visit_def(self, url):
        for nv in self.no_visit_default:
            if nv in url:
                return False
        return True

    def _remove_divs(self, soup, attrs, values):
        for attribute in attrs:
            for v in values:
                for div in soup.findAll(attrs={attribute: v}):
                    div.decompose()

    def clean_html(self, soup):
        try:

            tit = soup.find('title')

            title = ""
            if tit is not None:
                title = tit.string
                tit.decompose()

            tags = ["footer", "header", "nav", "form", "style", "meta", "script"]
            for tag in tags:
                for div in soup.find_all(tag):
                    div.decompose()

            attrs = ["class", "id"]
            tags = ["footer", "Footer", "nav", "Nav", "banner", "Banner", "box", "Box", "pie", "Pie", "rightBlock", "menu",
                    "block-menu"]
            self._remove_divs(soup, attrs, tags)

            for x in soup.find_all("p"):
                text = x.get_text()
                if len(text.split(" ")) < 5 or "cookies" in text:
                    x.decompose()

            texto = '. '.join(soup.stripped_strings)
            texto = texto.replace("..", ".")

            return title, texto

        except Exception as e:
            logging.exception("Error during HTML cleaning")
            return None, None

    def build_uri_id(self, url):

        try:
            # usamos este diccionario para acortar la longitud de la url codificada
            diccionario = {"https://transparencia.aragon.es": "11",
                        "https://www.saludinforma.es": "12",
                        "https://educa.aragon.es": "13",
                        "https://www.turismodearagon.com": "14",
                        "https://acpua.aragon.es": "15",
                        "https://www.aragon.es": "16",
                        "https://www.aragonhoy.net": "17"}
            prefix = "99"
            sector_temp = "sector-publico"

            if self.sectores_map is not None:
                for key in self.sectores_map:
                    if url.startswith(key):
                        sector_temp = self.sectores_map[key]
                        break

            path_input_string = url

            for key in diccionario:
                if url.startswith(key):
                    path_input_string = url[len(key):]
                    prefix = diccionario[key]

            uri_temp = prefix + base64.urlsafe_b64encode(path_input_string.encode('utf-8')).decode('utf-8').replace("=", "")
            return uri_temp, sector_temp

        except Exception as e:
            logging.exception(f"Error generating URI ID for URL {url}")
            return None, None

    def summarize_text(self, html):
        start_time = time.time()
        with self.tracer.start_as_current_span("Summarize Text") as span:
            try:
                summary_text = ""
                input_length = 0
                if html:
                    input_length = len(html)
                    summary_text = summarize(html,
                                            ratio=0.2,
                                            words=None,
                                            language='spanish',
                                            split=False,
                                            scores=False,
                                            additional_stopwords=None)

                span.set_attribute("input_length", input_length)
                span.set_attribute("summary_length", len(summary_text))
                span.set_status(StatusCode.OK)

                elapsed = time.time() - start_time
                
                self.summarize_execution_time.record(elapsed)

                span.set_attribute("time", elapsed)

                return summary_text.replace("'", " ")

            except Exception as e:
                span.record_exception(e)
                span.set_status(Status(StatusCode.ERROR, "Error during text summarization"))
                logging.exception("Error during text summarization")
                return ""

    def pdf_to_text(self, content):
        start_time = time.time()
        with self.tracer.start_as_current_span("PDF to Text Extraction") as span:

            try:
                num_pages = 0
                span.set_attribute("pdf_size", len(content))


                all_pages = ""
                doc = fitz.open(stream=content, filetype="pdf")
                title = doc.metadata["title"]


                span.set_attribute("title", title)
                for page in doc:
                    all_pages += page.get_text()
                    num_pages += num_pages

                span.set_attribute("num_pages", num_pages)
                span.add_event("PDF text extraction completed")

                span.set_status(StatusCode.OK)

                elapsed = time.time() - start_time
                self.pdf_extraction_time.record(elapsed)
                return title, all_pages
            
            except Exception as e:
                span.record_exception(e)
                span.set_status(Status(StatusCode.ERROR, "Error extracting PDF text"))
                logging.exception("Error during PDF text extraction")
                return None, None

    def check_webpage_changes(self, newcrc, sector, uri_id):

        start_time = time.time()

        oldcrc = 0
        has_changed = True
        try:
            query = "PREFIX schema: <http://schema.org/>  PREFIX recurso: <http://opendata.aragon.es/recurso/" + sector + "/documento/webpage/>  select ?crc  from <http://opendata.aragon.es/def/ei2av2> where  {  recurso:" + uri_id + " schema:version   ?crc}"

            data = self.sparql_helper.query(self.sparql_user, self.sparql_pass, self.sparql_server,
                                        self.sparql_path_auth, self.querystring, query)
            lines = data["results"]["bindings"]

            if lines is not None and len(lines) > 0:
                oldcrc = lines[0]["crc"]["value"]
                span.set_attribute("old_crc", oldcrc)

            if oldcrc == str(newcrc):
                has_changed = False

        except Exception as e:
            has_changed = True
            logging.exception(f"Error while checking webpage changes for uri_id={uri_id}, sector={sector}")

        elapsed = time.time() - start_time
        self.check_webpage_changes_execution_time.record(elapsed, {"sector": sector})

        return has_changed

    def delete_old_values(self, sector, uri_id):


        with self.tracer.start_as_current_span("Delete Old Values") as span:
            span.set_attribute("sector", sector)
            span.set_attribute("uri_id", uri_id)

            query = "PREFIX recurso: <http://opendata.aragon.es/recurso/" + sector + "/documento/webpage/> DELETE WHERE { GRAPH <http://opendata.aragon.es/def/ei2av2> {recurso:" + uri_id + " ?x ?y } }"
            span.add_event("SPARQL Query Constructed", {"query_length": len(query)})

            try:
                span.add_event("Initiating SPARQL Delete Operation")
                start_time = time.time()

                self.sparql_helper.query(self.sparql_user, self.sparql_pass, self.sparql_server, self.sparql_path_auth,
                                self.querystring, query)

                execution_time = time.time() - start_time
                self.delete_old_values_execution_time.record(execution_time, {"operation": "delete", "sector": sector})

                span.set_attribute("query", query)
                span.add_event("SPARQL Delete Operation Done")

                span.set_attribute("execution_time_seconds", execution_time)
                span.set_status(StatusCode.OK)
                #logging.info(f"Successfully deleted old values for sector={sector}, uri_id={uri_id}")

            except Exception as e:
                span.record_exception(e)
                span.set_status(Status(StatusCode.ERROR, "Error during SPARQL delete operation"))
                logging.exception(f"Error while deleting old values for sector={sector}, uri_id={uri_id}: {e}")

    def insert_data(self, uri_id, sector, url, crc, title, summary, texto):


        start_time = time.time()

        with self.tracer.start_as_current_span("Insert SPARQL Data") as span:
            span.set_attribute("uri_id", uri_id)
            span.set_attribute("sector", sector)
            span.set_attribute("url", url)
            span.set_attribute("crc", crc)
            span.set_attribute("title_length", len(title))
            span.set_attribute("summary_length", len(summary))

            try:
                span.add_event("Processing input text")

                query = "PREFIX schema: <http://schema.org/>   PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> "
                query = f"{query} PREFIX owl: <http://www.w3.org/2002/07/owl#>  PREFIX recurso: <http://opendata.aragon.es/recurso/{sector}/documento/webpage/> "
                query = f"{query} PREFIX nti: <http://datos.gob.es/kos/sector-publico/sector/> PREFIX dcat: <http://www.w3.org/ns/dcat#> "
                query = f"{query} INSERT DATA {{ GRAPH <http://opendata.aragon.es/def/ei2av2> {{ "
                query = f"{query}  recurso:{uri_id} rdf:type schema:CreativeWork . "
                query = f"{query}  recurso:{uri_id} rdf:type owl:NamedIndividual  . "
                query = f"{query}  recurso:{uri_id} schema:url  <{url}>  . "
                query = f"{query}  recurso:{uri_id} schema:title '{title}'  ."
                query = f"{query}  recurso:{uri_id} schema:version '{str(crc)}' . "
                query = f"{query}  recurso:{uri_id} schema:abstract '{summary}' . "
                query = f"{query}  recurso:{uri_id} schema:concept nti:{sector} . "
                query = f"{query}  recurso:{uri_id} dcat:theme nti:{sector} . "
                query = f"{query}  recurso:{uri_id} schema:sdDatePublished   '{datetime.now().strftime('%Y%m%d')}' "

                textosinacentos = sparqlhelper.eliminar_acentos(texto)
                textosinespaciosmultiples = str(re.sub(' +', ' ', textosinacentos))
                added_ids = set()

                for map in self.maps:
                    for key in map:
                        if key in textosinespaciosmultiples:
                            pattern = r'\b' + key + r'\b'
                            match = re.search(pattern, textosinespaciosmultiples.replace(".", " "))
                            if match is not None and map[key] not in added_ids:
                                # no incluir duplicados de uris iguales que puedan tener distinto nombre
                                added_ids.add(map[key])
                                query = f"{query} . recurso:{uri_id} schema:about <{map[key]}> "

                span.add_event("SPARQL Query Constructed", {"query_length": len(query)})


            except Exception as e:
                logging.exception(f"Error {e} while constructing the SPARQL query: {query}")
                span.record_exception(e)
                span.set_status(Status(StatusCode.ERROR, "Error constructing SPARQL query"))
                return None

            try:
                span.add_event("Inserting data into Virtuoso")
                span.set_attribute("query", query)
                start_time = time.time()

                query = f"{query} }} }}"
                            
                result = self.sparql_helper.insertdata(
                    self.sparql_user, self.sparql_pass,
                    self.sparql_server, self.sparql_path_auth,
                    self.querystring, query
                )

                execution_time = time.time() - start_time
                self.insert_execution_time.record(execution_time, {"sector": sector})
                self.successful_insertions.add(1, {"sector": sector})

                span.set_attribute("execution_time_seconds", execution_time)
                span.set_status(StatusCode.OK)

                return result

            except Exception as e:
                span.record_exception(e)
                span.set_status(Status(StatusCode.ERROR, "Error inserting data into Virtuoso"))
                logging.exception(f"Error {e} while inserting SPARQL data")
                return None

            finally:
                total_elapsed = time.time() - start_time
                self.insert_data_time.record(total_elapsed, {"sector": sector})

        #query = f"{query} }} }}"
        #return (self.sparql_helper.insertdata(self.sparql_user, self.sparql_pass, self.sparql_server, self.sparql_path_auth,self.querystring, query))

    def crawl(self, url):

        if not hasattr(self, 'crawl_time'):
            self.crawl_time = self.meter.create_histogram(
                "crawl_execution_time",
                description="Tiempo de ejecución de la función crawl(url) en segundos"
            )

        crawl_start = time.time()

        with self.tracer.start_as_current_span(f'Crawl {url}') as span:
            span.set_attribute("url", url)

            try:

                response = requests.get(url)
                span.set_attribute("status", response.status_code)

                if response.status_code == 200:
                    
                    headers = response.headers

                    uri_id, sector = self.build_uri_id(url)
                    span.set_attribute("uri_id", uri_id)
                    span.set_attribute("sector", sector)

                    content_type = str(headers['content-type'])
                    has_changed = True
                    new_crc = 0
                    titulo = ""
                    texto = ""
                    domain = urlparse(url).netloc
                    domain = domain.replace("www.", "")
                    raw_text = ""
                    if "text" in content_type:  # aunque se descartan ciertas extensiones pueden venir datos en formatos no deseados
                        raw_text = response.text
                        soup = BeautifulSoup(raw_text, 'html.parser')
                        titulo, texto = self.clean_html(soup)
                        
                        span.set_attribute("titulo", titulo)
                        span.set_attribute("texto", texto)

                        new_crc = zlib.crc32(texto.encode('utf-8'))
                        # si no es pdf busca los enlaces y los añadimos a la lista de url a procesar
                        for url_temp in self.get_linked_urls(url, soup):
                            try:
                                if url_temp is not None and domain in url_temp:
                                    domain_temp = urlparse(url_temp).netloc
                                    domain_temp = domain_temp.replace("www.", "")
                                    if domain == domain_temp:
                                        self.add_url_to_visit(url_temp)
                            except Exception as e:
                                logging.exception(f"Error while processing URL {url_temp}: {e}")
                    elif "pdf" in content_type:
                        # calcula el crc para ver si ha cambiado lo que hay en la bd
                        try:
                            content_length = str(headers['content-length'])
                            if int(str(content_length)) < 1024 * 1024:  # solo procesamos los pdf menores de 1MB
                                new_crc = zlib.crc32(response.content)
                            else:
                                #logging.info("Archivo pdf descartado")
                                return
                        except Exception as e:
                            logging.exception(f"Error while processing PDF content length for URL {url}: {e}")
                            return
                    else:
                        return
                    # comprueba en la bd si ha habido cambios
                    # si no existe se devuelve true 
                    has_changed = self.check_webpage_changes(new_crc, sector, uri_id)
                    span.set_attribute("has_changed", has_changed)

                    self.processed += 1

                    if has_changed:
                        # extrae el contenido
                        if "pdf" in content_type:
                            titulo, texto = self.pdf_to_text(response.content)

                            # resume el contenido
                        summary = self.summarize_text(texto)
                        summary = summary.replace("\n", " ")
                        summary = re.sub(' +', ' ', summary)  # eliminamos los espacios multiples
                        # borra los datos antiguos
                        
                        self.delete_old_values(sector, uri_id)
                        self.insert_data(uri_id, sector, url, new_crc, titulo, summary, texto)
                        self.added += 1
            except Exception as e:
                logging.exception(f"Error during crawling URL {url}: {e}")
            finally:
                elapsed = time.time() - crawl_start
                self.crawl_time.record(elapsed, {"url": url})
                
    def run(self):

        if not hasattr(self, 'total_run_time'):
            self.total_run_time = self.meter.create_histogram(
                "crawler_run_execution_time",
                description="Tiempo total de ejecución del run() del crawler en segundos"
            )

        start_time = time.time()

        errors_total = 0
        urls_processed_total = 0 

                
        try:
            while self.urls_to_visit:
                try:
                    url = self.urls_to_visit.pop(0)
                    self.crawl(url)
                    urls_processed_total += 1
                except Exception:
                    errors_total += 1
                    logging.exception(f'Failed to crawl: {url}')
                finally:
                    if url:
                        self.visited_urls.append(url)
            self.endtime = time.time()

            logging.info(f'SUMMARY:  processed: {self.processed}  added:{self.added}')
            logging.info(f'TIME:  {str(self.endtime - self.starttime)} seconds')

        except Exception as e:
            logging.exception("Critical error during crawl execution.")
        finally:
            total_elapsed = time.time() - start_time
            self.total_run_time.record(total_elapsed)


if __name__ == '__main__':
    Crawler().run()

    # crawler = Crawler().run()
    # crawler.crawl("http://www.patrimonioculturaldearagon.es/agenda-portada/primera-temporada-de-lirica-y-danza-2021")