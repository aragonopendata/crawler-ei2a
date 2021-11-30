no_visit = ["https://www.saludinforma.es/portalsi/web/salud/agenda",
                    "https://www.saludinforma.es/edsformacion/calendar",
                    "https://www.saludinforma.es/edsformacion/?time=", 
                    "https://transparencia.aragon.es/transparencia/declaraciones/JavierCenarroLagunas.pdf"]

urlsfile='urls.csv'

urls={"https://transparencia.aragon.es":"sector-publico",
        "https://www.saludinforma.es":"salud",
        "https://educa.aragon.es/":"educacion",
        "https://www.turismodearagon.com/es/":"turismo",
        "https://acpua.aragon.es/":"educacion",
        "https://arasaac.org/":"sociedad-bienestar",
        "http://patrimonioculturaldearagon.es/":"cultura-ocio",
        "http://www.sarga.es":"medio-ambiente",
        "https://inaem.aragon.es/":"empleo",
        "https://sda.aragon.es/":"ciencia-tecnologia",
        "https://aragoncircular.es/":"economia"
}


sparql_user='cargaslote3'
sparql_pass='gJCbboEb2mT8qSzn'
sparql_server='http://biv-aodback-01.aragon.local:8890'
sparql_path='/sparql'
sparql_path_auth='/sparql-auth'
querystring='?default-graph-uri=&should-sponge=&timeout=0&signal_void=on'