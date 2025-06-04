import base64
import csv
# import logger
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



import json
from opentelemetry import trace
import logging

def setup_structured_logging():
    """
    Configura logging estructurado que correlaciona con las trazas de OpenTelemetry
    """
    class JsonFormatter(logging.Formatter):
        def format(self, record):
            # Obtener el contexto de la traza actual si está disponible
            current_span = trace.get_current_span()
            span_context = current_span.get_span_context() if current_span else None
            
            # Convertir trace_id y span_id a formato hexadecimal si están disponibles
            trace_id = f"{span_context.trace_id:032x}" if span_context and span_context.trace_id else ""
            span_id = f"{span_context.span_id:016x}" if span_context and span_context.span_id else ""
            
            log_record = {
                "timestamp": datetime.utcnow().isoformat(),
                "level": record.levelname,
                "logger": record.name,
                "message": record.getMessage(),
                "trace_id": trace_id,
                "span_id": span_id
            }
            
            # Incluir excepciones si las hay
            if record.exc_info:
                log_record["exception"] = self.formatException(record.exc_info)
            
            # Incluir información adicional si existe
            if hasattr(record, 'url'):
                log_record["url"] = record.url
            if hasattr(record, 'uri_id'):
                log_record["uri_id"] = record.uri_id
            if hasattr(record, 'sector'):
                log_record["sector"] = record.sector
            
            return json.dumps(log_record)
    
    # Crear handler con formato JSON
    json_handler = logging.StreamHandler()
    json_handler.setFormatter(JsonFormatter())
    
    # Configurar logger raíz
    root_logger = logging.getLogger()
    root_logger.handlers = [json_handler]  # Reemplazar handlers existentes
    root_logger.setLevel(logging.INFO)
    
    return root_logger


load_dotenv()
logger = setup_structured_logging()

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
        self.meter = OpenTelemetryConfig.get_meter("crawler_metrics")

        self.urls_processed_counter = self.meter.create_counter(
            "urls_processed",
            description="Número de URLs procesadas",
            unit="1"
        )
        
        self.urls_changed_counter = self.meter.create_counter(
            "urls_changed",
            description="Número de URLs que han cambiado y se han actualizado",
            unit="1"
        )
        
        self.sparql_errors_counter = self.meter.create_counter(
            "sparql_errors",
            description="Número de errores SPARQL durante inserciones",
            unit="1"
        )
        
        # Histograma para tiempos de procesamiento
        self.crawl_duration = self.meter.create_histogram(
            "crawl_duration",
            description="Tiempo de procesamiento de cada URL",
            unit="s"
        )

        # Métricas para operaciones SPARQL
        self.sparql_operation_counter = self.meter.create_counter(
            "sparql_operations",
            description="Número de operaciones SPARQL ejecutadas",
            unit="1"
        )

        self.sparql_error_counter = self.meter.create_counter(
            "sparql_errors",
            description="Número de errores SPARQL",
            unit="1"
        )

        self.sparql_operation_duration = self.meter.create_histogram(
            "sparql_operation_duration",
            description="Tiempo de ejecución de operaciones SPARQL",
            unit="s"
        )

        # Agregador para urls procesadas por sector
        self.urls_by_sector = self.meter.create_up_down_counter(
            "urls_by_sector",
            description="Número de URLs procesadas por sector",
            unit="1"
        )
        
        self.session = requests.Session()
        self.session.max_redirects = 10
        self.session.timeout = 30

        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'es-ES,es;q=0.8,en-US;q=0.5,en;q=0.3',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive'
        })

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
            logger.exception("Error loading URLs")

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

    def escape_sparql_string(self, text):
        """
        Escapa caracteres especiales para strings en SPARQL
        """
        if text is None:
            return ""
        
        # Convertir a string si no lo es
        text = str(text)
        
        # Escapar caracteres especiales
        text = text.replace("\\", "\\\\")  # Escapar backslashes primero
        text = text.replace("'", "\\'")   # Escapar comillas simples
        text = text.replace('"', '\\"')   # Escapar comillas dobles
        text = text.replace("\n", "\\n")  # Escapar saltos de línea
        text = text.replace("\r", "\\r")  # Escapar retornos de carro
        text = text.replace("\t", "\\t")  # Escapar tabulaciones
        
        # Eliminar caracteres de control adicionales
        text = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', text)
        
        return text

    def clean_text_for_sparql(self, text):
        """
        Limpia texto para uso seguro en SPARQL
        """
        if text is None:
            return ""
        
        text = str(text).strip()
        
        # Normalizar espacios en blanco
        text = re.sub(r'\s+', ' ', text)
        
        # Eliminar caracteres problemáticos
        text = re.sub(r'[^\w\s\-.,;:!?()áéíóúüñÁÉÍÓÚÜÑ]', ' ', text)
        
        # Limitar longitud
        if len(text) > 1000:
            text = text[:997] + "..."
        
        return self.escape_sparql_string(text)

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
            logger.exception("Error during linked URL extraction")
        finally:
            elapsed = time.time() - start_time

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
                title = tit.get_text().strip()
                # Limpiar el título
                title = re.sub(r'\s+', ' ', title)
                title = title[:200] if len(title) > 200 else title  # Limitar longitud
                tit.decompose()

            tags = ["footer", "header", "nav", "form", "style", "meta", "script"]
            for tag in tags:
                for div in soup.find_all(tag):
                    div.decompose()

            attrs = ["class", "id"]
            tags = ["footer", "Footer", "nav", "Nav", "banner", "Banner", "box", "Box", "pie", "Pie", "rightBlock", "menu", "block-menu"]
            self._remove_divs(soup, attrs, tags)

            for x in soup.find_all("p"):
                text = x.get_text()
                if len(text.split(" ")) < 5 or "cookies" in text.lower():
                    x.decompose()

            texto = '. '.join(soup.stripped_strings)
            texto = texto.replace("..", ".")
            
            # Limpiar texto
            texto = re.sub(r'\s+', ' ', texto)
            texto = texto.strip()

            return title, texto

        except Exception as e:
            logging.exception("Error during HTML cleaning")
            return "", ""

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
            logger.exception(f"Error generating URI ID for URL {url}")
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
                span.set_attribute("time", elapsed)

                return summary_text.replace("'", " ")

            except Exception as e:
                span.record_exception(e)
                span.set_status(Status(StatusCode.ERROR, "Error during text summarization"))
                logger.exception("Error during text summarization")
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
                return title, all_pages
            
            except Exception as e:
                span.record_exception(e)
                span.set_status(Status(StatusCode.ERROR, "Error extracting PDF text"))
                logger.exception("Error during PDF text extraction")
                return None, None

    def check_webpage_changes(self, newcrc, sector, uri_id):
        with self.tracer.start_as_current_span("Check Webpage Changes") as span:
            span.set_attribute("uri_id", uri_id)
            span.set_attribute("sector", sector)
            span.set_attribute("new_crc", newcrc)
            
            start_time = time.time()
            oldcrc = 0
            has_changed = True
            
            try:
                query = f"""PREFIX schema: <http://schema.org/>  
                        PREFIX recurso: <http://opendata.aragon.es/recurso/{sector}/documento/webpage/>  
                        SELECT ?crc FROM <http://opendata.aragon.es/def/ei2av2> 
                        WHERE {{ recurso:{uri_id} schema:version ?crc }}"""
                
                params = {"uri_id": uri_id, "sector": sector}
                
                # Usar nuestro helper para la consulta
                data = self.sparql_helper_with_tracing("query", query, params)
                
                lines = data["results"]["bindings"]
                
                if lines is not None and len(lines) > 0:
                    oldcrc = lines[0]["crc"]["value"]
                    span.set_attribute("old_crc", oldcrc)
                
                if oldcrc == str(newcrc):
                    has_changed = False
                
                span.set_attribute("has_changed", has_changed)
                return has_changed
                
            except Exception as e:
                has_changed = True  # En caso de error, asumimos que ha cambiado
                span.record_exception(e)
                span.set_attribute("error", str(e))
                span.set_status(Status(StatusCode.ERROR, f"Error checking webpage changes: {str(e)}"))
                logger.error(f"Error checking webpage changes", 
                            exc_info=True,
                            extra={"uri_id": uri_id, "sector": sector})
                return has_changed
                
            finally:
                elapsed = time.time() - start_time
                span.set_attribute("duration_seconds", elapsed)

    def delete_old_values(self, sector, uri_id):
        with self.tracer.start_as_current_span("Delete Old Values") as span:
            span.set_attribute("uri_id", uri_id)
            span.set_attribute("sector", sector)
            
            query = f"""PREFIX recurso: <http://opendata.aragon.es/recurso/{sector}/documento/webpage/> 
                    DELETE WHERE {{ 
                        GRAPH <http://opendata.aragon.es/def/ei2av2> {{
                            recurso:{uri_id} ?x ?y 
                        }} 
                    }}"""
            
            try:
                params = {"uri_id": uri_id, "sector": sector}
                self.sparql_helper_with_tracing("delete", query, params)
                span.set_status(StatusCode.OK)
                return True
                
            except Exception as e:
                span.record_exception(e)
                span.set_status(Status(StatusCode.ERROR, f"Error deleting old values: {str(e)}"))
                logger.error(f"Error deleting old values", 
                            exc_info=True,
                            extra={"uri_id": uri_id, "sector": sector})
                return False

    def safe_set_span_attribute(self, span, attribute_name, value):
        """
        Establece un atributo de span de forma segura, manejando valores None
        """
        if value is None:
            value = ""
        elif not isinstance(value, (str, int, float, bool)):
            value = str(value)
        
        try:
            span.set_attribute(attribute_name, value)
        except Exception as e:
            logging.warning(f"Could not set span attribute {attribute_name}: {e}")

    def insert_data(self, uri_id, sector, url, crc, title, summary, texto):
        start_time = time.time()

        with self.tracer.start_as_current_span("Insert SPARQL Data") as span:
            span.set_attribute("uri_id", uri_id)
            span.set_attribute("sector", sector)
            span.set_attribute("url", url)
            span.set_attribute("crc", crc)
            
            # Verificar y limpiar inputs
            if title is None:
                title = ""
            if summary is None:
                summary = ""
            if texto is None:
                texto = ""
                
            # Limpiar los textos para SPARQL
            clean_title = self.clean_text_for_sparql(title)
            clean_summary = self.clean_text_for_sparql(summary)
            clean_texto = self.clean_text_for_sparql(texto)
            
            # NUEVA LÍNEA: Limpiar la URL para eliminar saltos de línea y espacios
            clean_url = url.strip().replace('\n', '').replace('\r', '').replace('\t', '')
            
            span.set_attribute("title_length", len(clean_title))
            span.set_attribute("summary_length", len(clean_summary))

            try:
                span.add_event("Processing input text")

                # Construir la query con strings seguros
                query_parts = [
                    "PREFIX schema: <http://schema.org/>",
                    "PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>",
                    "PREFIX owl: <http://www.w3.org/2002/07/owl#>",
                    f"PREFIX recurso: <http://opendata.aragon.es/recurso/{sector}/documento/webpage/>",
                    "PREFIX nti: <http://datos.gob.es/kos/sector-publico/sector/>",
                    "PREFIX dcat: <http://www.w3.org/ns/dcat#>",
                    "INSERT DATA { GRAPH <http://opendata.aragon.es/def/ei2av2> {",
                    f"  recurso:{uri_id} rdf:type schema:CreativeWork .",
                    f"  recurso:{uri_id} rdf:type owl:NamedIndividual .",
                    f"  recurso:{uri_id} schema:url <{clean_url}> .",  # USAR URL LIMPIA
                    f"  recurso:{uri_id} schema:title '{clean_title}' .",
                    f"  recurso:{uri_id} schema:version '{str(crc)}' .",
                    f"  recurso:{uri_id} schema:abstract '{clean_summary}' .",
                    f"  recurso:{uri_id} schema:concept nti:{sector} .",
                    f"  recurso:{uri_id} dcat:theme nti:{sector} .",
                    f"  recurso:{uri_id} schema:sdDatePublished '{datetime.now().strftime('%Y%m%d')}'"
                ]

                # Procesar entidades encontradas en el texto
                textosinacentos = sparqlhelper.eliminar_acentos(clean_texto)
                textosinespaciosmultiples = str(re.sub(' +', ' ', textosinacentos))
                added_ids = set()

                for map in self.maps:
                    for key in map:
                        if key in textosinespaciosmultiples:
                            pattern = r'\b' + re.escape(key) + r'\b'
                            match = re.search(pattern, textosinespaciosmultiples.replace(".", " "))
                            if match is not None and map[key] not in added_ids:
                                added_ids.add(map[key])
                                query_parts.append(f"  . recurso:{uri_id} schema:about <{map[key]}>")

                query_parts.append("} }")
                query = " ".join(query_parts)

                span.add_event("SPARQL Query Constructed", {"query_length": len(query)})

            except Exception as e:
                logging.exception(f"Error constructing SPARQL query: {e}")
                span.record_exception(e)
                span.set_status(Status(StatusCode.ERROR, "Error constructing SPARQL query"))
                return None

            try:
                span.add_event("Inserting data into Virtuoso")
                span.set_attribute("query", query)
                
                result = self.sparql_helper.insertdata(
                    self.sparql_user, self.sparql_pass,
                    self.sparql_server, self.sparql_path_auth,
                    self.querystring, query
                )

                execution_time = time.time() - start_time
                span.set_attribute("execution_time_seconds", execution_time)
                span.set_status(StatusCode.OK)

                return result

            except Exception as e:
                span.record_exception(e)
                span.set_status(Status(StatusCode.ERROR, "Error inserting data into Virtuoso"))
                logging.exception(f"Error inserting SPARQL data: {e}")
                return None

            finally:
                total_elapsed = time.time() - start_time

    def crawl(self, url):
        crawl_start = time.time()

        with self.tracer.start_as_current_span(f'Crawl {url}') as span:
            span.set_attribute("url", url)

            try:
                response = self.session.get(url, timeout=30, allow_redirects=True)
                span.set_attribute("status", response.status_code)

                if response.url != url:
                    self.safe_set_span_attribute(span, "final_url", response.url)
                    logging.info(f"URL redirected from {url} to {response.url}")

                if response.status_code == 200:
                    headers = response.headers
                    uri_id, sector = self.build_uri_id(url)
                    
                    self.safe_set_span_attribute(span, "uri_id", uri_id)
                    self.safe_set_span_attribute(span, "sector", sector)

                    content_type = str(headers.get('content-type', ''))
                    has_changed = True
                    new_crc = 0
                    titulo = ""
                    texto = ""
                    domain = urlparse(url).netloc.replace("www.", "")
                    
                    if "text" in content_type:
                        raw_text = response.text
                        soup = BeautifulSoup(raw_text, 'html.parser')
                        titulo, texto = self.clean_html(soup)
                        
                        # Asegurar que titulo y texto no sean None
                        titulo = titulo if titulo is not None else ""
                        texto = texto if texto is not None else ""
                        
                        self.safe_set_span_attribute(span, "titulo", titulo)
                        self.safe_set_span_attribute(span, "texto_length", len(texto))

                        new_crc = zlib.crc32(texto.encode('utf-8'))
                        
                        # Procesar enlaces
                        for url_temp in self.get_linked_urls(url, soup):
                            try:
                                if url_temp is not None and domain in url_temp:
                                    domain_temp = urlparse(url_temp).netloc.replace("www.", "")
                                    if domain == domain_temp:
                                        self.add_url_to_visit(url_temp)
                            except Exception as e:
                                logging.exception(f"Error processing URL {url_temp}: {e}")
                                
                    elif "pdf" in content_type:
                        try:
                            content_length = headers.get('content-length', '0')
                            if int(content_length) < 1024 * 1024:  # solo procesamos PDFs < 1MB
                                new_crc = zlib.crc32(response.content)
                            else:
                                return
                        except Exception as e:
                            logging.exception(f"Error processing PDF content length for URL {url}: {e}")
                            return
                    else:
                        return
                    
                    # Verificar cambios
                    has_changed = self.check_webpage_changes(new_crc, sector, uri_id)
                    self.safe_set_span_attribute(span, "has_changed", has_changed)

                    self.processed += 1

                    if has_changed:
                        if "pdf" in content_type:
                            titulo, texto = self.pdf_to_text(response.content)
                            # Asegurar que no sean None
                            titulo = titulo if titulo is not None else ""
                            texto = texto if texto is not None else ""

                        summary = self.summarize_text(texto)
                        summary = summary.replace("\n", " ") if summary else ""
                        summary = re.sub(' +', ' ', summary)
                        
                        self.delete_old_values(sector, uri_id)
                        self.insert_data(uri_id, sector, url, new_crc, titulo, summary, texto)
                        self.added += 1
                    pass
                else:
                    logging.warning(f"HTTP {response.status_code} for URL: {url}")
                    return
            except requests.exceptions.TooManyRedirects:
                logging.warning(f"Too many redirects for URL: {url}")
                span.set_attribute("error", "too_many_redirects")
                # Marcar URL como no visitable
                self.no_visit.append(url)
                return
            except requests.exceptions.Timeout:
                logging.warning(f"Timeout for URL: {url}")
                span.set_attribute("error", "timeout")
                return
            except requests.exceptions.ConnectionError:
                logging.warning(f"Connection error for URL: {url}")
                span.set_attribute("error", "connection_error")
                return
            except Exception as e:
                logging.exception(f"Error crawling URL {url}: {e}")
                span.record_exception(e)
                return
            finally:
                elapsed = time.time() - crawl_start
                self.safe_set_span_attribute(span, "crawl_time", elapsed)

    def _check_sparql_connectivity(self):
        """
        Verifica la conectividad básica con el servidor SPARQL
        """
        try:
            simple_query = "SELECT ?s WHERE { ?s ?p ?o } LIMIT 1"
            result = self.sparql_helper.query(
                self.sparql_user, self.sparql_pass,
                self.sparql_server, self.sparql_path_auth,
                self.querystring, simple_query
            )
            return result is not None and "results" in result
        except Exception as e:
            logger.error(f"Connectivity check failed: {e}")
            return False

    def sparql_helper_with_tracing(self, operation_type, query, params=None):
        """
        Ejecuta operaciones SPARQL con trazabilidad mejorada y manejo robusto de errores.
        """
        with self.tracer.start_as_current_span(f"SPARQL_{operation_type}") as span:
            # Atributos comunes
            span.set_attribute("query", query[:500] if len(query) > 500 else query)  # Limitar tamaño
            
            # Si tenemos parámetros, los agregamos
            if params:
                for key, value in params.items():
                    span.set_attribute(key, str(value)[:100])  # Limitar tamaño
            
            start_time = time.time()
            
            try:
                # Ejecutar la operación según su tipo
                if operation_type == "insert":
                    result = self.sparql_helper.insertdata(
                        self.sparql_user, self.sparql_pass,
                        self.sparql_server, self.sparql_path_auth,
                        self.querystring, query
                    )
                elif operation_type == "query":
                    result = self.sparql_helper.query(
                        self.sparql_user, self.sparql_pass,
                        self.sparql_server, self.sparql_path_auth,
                        self.querystring, query
                    )
                elif operation_type == "delete":
                    result = self.sparql_helper.query(
                        self.sparql_user, self.sparql_pass,
                        self.sparql_server, self.sparql_path_auth,
                        self.querystring, query
                    )
                else:
                    raise ValueError(f"Tipo de operación SPARQL desconocido: {operation_type}")
                
                # Registrar éxito
                span.set_attribute("success", True)
                span.set_attribute("result_code", result if isinstance(result, int) else 200)
                
                # Métricas para operaciones exitosas
                query_type_label = {"operation": operation_type}
                self.sparql_operation_counter.add(1, query_type_label)
                
                # Tiempo de ejecución
                execution_time = time.time() - start_time
                span.set_attribute("execution_time_seconds", execution_time)
                self.sparql_operation_duration.record(execution_time, query_type_label)
                
                # Log estructurado
                logger.info(f"SPARQL {operation_type} successful", 
                            extra={"operation": operation_type, "execution_time": execution_time})
                
                return result
                
            except Exception as e:
                error_message = str(e)
                
                # Extraer información de errores Virtuoso
                virtuoso_error_match = re.search(r"Virtuoso (\d+) Error ([A-Z0-9]+): (.+)", error_message)
                if virtuoso_error_match:
                    error_code = virtuoso_error_match.group(2)
                    error_details = virtuoso_error_match.group(3)
                    
                    span.set_attribute("virtuoso_error_code", error_code)
                    span.set_attribute("virtuoso_error_details", error_details[:200])  # Limitar tamaño
                    
                    # Buscar detalles de errores de sintaxis
                    syntax_error_match = re.search(r"syntax error at ['\"]([^'\"]+)['\"] before ['\"]([^'\"]+)['\"]", error_details)
                    if syntax_error_match:
                        error_at = syntax_error_match.group(1)
                        error_before = syntax_error_match.group(2)
                        span.set_attribute("syntax_error_at", error_at)
                        span.set_attribute("syntax_error_before", error_before)
                
                # Registrar error
                span.record_exception(e)
                span.set_attribute("success", False)
                span.set_status(Status(StatusCode.ERROR, error_message))
                
                # Métricas para operaciones fallidas
                error_type = type(e).__name__
                error_labels = {"operation": operation_type, "error_type": error_type}
                self.sparql_error_counter.add(1, error_labels)
                
                # Log estructurado
                logger.error(f"SPARQL {operation_type} failed: {error_message}", 
                            exc_info=True,
                            extra={"operation": operation_type, "error_type": error_type})
                
                # Guardar consulta fallida para diagnóstico
                self._save_failed_query(query, error_message, params)
                
                # En lugar de re-lanzar la excepción, retornar valores por defecto
                if operation_type == "query":
                    return {"results": {"bindings": []}}
                else:
                    return 500

    def _save_failed_query(self, query, error_message, params=None):
        """Guarda una consulta SPARQL fallida para diagnóstico posterior"""
        try:
            error_log_dir = "sparql_error_logs"
            os.makedirs(error_log_dir, exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{error_log_dir}/error_{timestamp}.sparql"
            
            with open(filename, "w") as f:
                f.write(f"# Error: {error_message}\n")
                if params:
                    f.write(f"# Parameters: {json.dumps(params)}\n")
                f.write("\n# Query:\n")
                f.write(query)
            
            logger.info(f"Failed SPARQL query saved to {filename}")
            
        except Exception as e:
            logger.error(f"Could not save failed SPARQL query: {e}")

    def run(self):
        """
        Método run mejorado con mejor manejo de errores y shutdown correcto
        """
        start_time = time.time()
        
        errors_total = 0
        urls_processed_total = 0
        consecutive_errors = 0
        max_consecutive_errors = 10  # Límite de errores consecutivos
        
        try:
            while self.urls_to_visit:
                url = None
                try:
                    url = self.urls_to_visit.pop(0)
                    self.crawl(url)
                    urls_processed_total += 1
                    consecutive_errors = 0  # Reset contador de errores consecutivos
                    
                    # Pequeña pausa para no sobrecargar el servidor
                    time.sleep(0.1)
                    
                except Exception as e:
                    errors_total += 1
                    consecutive_errors += 1
                    logger.exception(f'Failed to crawl: {url}')
                    
                    # Si hay muchos errores consecutivos, hacer una pausa más larga
                    if consecutive_errors >= max_consecutive_errors:
                        logger.warning(f"Too many consecutive errors ({consecutive_errors}). Pausing for recovery...")
                        time.sleep(30)  # Pausa de 30 segundos
                        consecutive_errors = 0
                        
                        # Verificar conectividad básica
                        if not self._check_sparql_connectivity():
                            logger.error("SPARQL server appears to be down. Stopping crawler.")
                            break
                            
                finally:
                    if url:
                        self.visited_urls.append(url)
                        
            self.endtime = time.time()
            
            logger.info(f'SUMMARY: processed: {self.processed} added: {self.added} errors: {errors_total}')
            logger.info(f'TIME: {str(self.endtime - self.starttime)} seconds')
            
        except Exception as e:
            logger.exception("Critical error during crawl execution.")
        finally:
            total_elapsed = time.time() - start_time
            logger.info(f"Total execution time: {total_elapsed} seconds")
            
            # Cerrar correctamente OpenTelemetry
            try:
                from opentelemetry_config import OpenTelemetryConfig
                OpenTelemetryConfig.shutdown()
            except Exception as e:
                logger.error(f"Error during OpenTelemetry shutdown: {e}")
            
if __name__ == '__main__':
    Crawler().run()

    # crawler = Crawler().run()
    # crawler.crawl("http://www.patrimonioculturaldearagon.es/agenda-portada/primera-temporada-de-lirica-y-danza-2021")