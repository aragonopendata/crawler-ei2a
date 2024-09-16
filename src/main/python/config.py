no_visit = ["www.saludinforma.es/portalsi/web/salud/agenda",
                    "www.saludinforma.es/edsformacion/calendar",
                    "www.saludinforma.es/edsformacion/?time=", 
                    "transparencia.aragon.es/transparencia/declaraciones/JavierCenarroLagunas.pdf",
                    "aragonhoy.net/index.php/date",
                    "aragonhoy.net/index.php/mod.imagenes",
                    "aragonhoy.net/index.php/mod.videos",
                    "aragonhoy.net/index.php/mod.tags",
                    "aragonhoy.net/index.php/mod.documentos",
                    "aragonhoy.net/index.php/mod.podcasts",
                    "www.aragonhoy.es/intranet/image/",
                    "transparencia.aragon.es/COVID19_20",
                    "inaem.aragon.es/print/",
                    "www.turismodearagon.com/fr/",
                    "www.turismodearagon.com/zh-hant/",
                    "www.turismodearagon.com/de/",
                    "www.turismodearagon.com/it/",
                    "www.turismodearagon.com/ja/",
                    "www.turismodearagon.com/en/",
                    "www.turismodearagon.com/mi-viaje/",
                    "www.turismodearagon.com/como-llegar",
                    "/politica-privacidad/",
                    "condiciones-de-uso",
                    "perfil-del-contratante",
                    "cookie",
                    "aviso-legal",
                    "?redirect=",
                    "/image/image_gallery?"]

urlsfile='urls.csv'

urls={  "https://transparencia.aragon.es":"sector-publico",
        "https://www.saludinforma.es":"salud",
        "https://educa.aragon.es/":"educacion",
        "https://www.turismodearagon.com/es/":"turismo",
        "https://acpua.aragon.es/":"educacion",
        "https://arasaac.org/":"sociedad-bienestar",
        "https://patrimonioculturaldearagon.es/":"cultura-ocio",
        "https://www.sarga.es":"medio-ambiente",
        "https://inaem.aragon.es/":"empleo",
        "https://sda.aragon.es/":"ciencia-tecnologia",
        "https://aragoncircular.es/":"economia",
        "https://www.aragonhoy.es/":"sector-publico",
        "https://culturadearagon.es/":"cultura-ocio"
      
}

depth=5
#sparql_user='cargaslote3'
#sparql_pass='gJCbboEb2mT8qSzn'
#sparql_server='http://biv-aodback-01.aragon.local:8890'
sparql_path='/sparql'
sparql_path_auth='/sparql-auth'
querystring='?default-graph-uri=&should-sponge=&timeout=0&signal_void=on'