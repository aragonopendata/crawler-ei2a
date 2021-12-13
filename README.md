# crawler-ei2a

Este proyecto contiene las carpetas y archivos necesarios para desplegar la aplicación que realiza el rastreo de ciertos portales del Gobierno de Aragón

## Requisitos

Las librerias usadas en este proyecto y sus respectivas versiones se pueden ver en el archivo 'src/main/python/requirements.txt'.

src/main/docker : archvos de configuracion de la imagen de docker

src/main/python: codigo fuente del crawler

src/main/script : script para generar la imagen de docker y ejecutar el crawler dentro de la imagen. 


## Configuracion el archivo  'src/main/python/config.py' contiene las variables de configuración

#lista con la urls que no se quieren procesar
no_visit = ["https://www.saludinforma.es/portalsi/web/salud/agenda",
                    "https://www.saludinforma.es/edsformacion/calendar",
                    "https://www.saludinforma.es/edsformacion/?time=", 
                    "https://transparencia.aragon.es/transparencia/declaraciones/JavierCenarroLagunas.pdf"]
                    
#nombre del archivo que contiene las urls o dominios a crawlear

urlsfile='urls.csv'

#las urls a crawlear tambien se pueden especificar como un diccionario que contiene url:sector

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

#usuario del servidor de sparql

sparql_user=****

#contraseña del servidor de sparql

sparql_pass=***

#url del servidor de sparql

sparql_server=***

#path donde se encuentra el servicio de queries GET, sin autenticacion

sparql_path='/sparql'

#path donde se encuentra el servicio de queries POST, con autenticacion

sparql_path_auth='/sparql-auth'

## tras completar el fichero de configuracion hay que ejecutar para generar la imagen de docker  
desde la carpeta principal del proyecto ejecutar:

  sh src/main/script/build.sh
  
para lanzar el crawler en la imagen creada 

  sh src/main/script/run.sh
  
una vez que el crawler a procesado todas las web el contenedor docker desaparece.

## LOG los mensajes de log se insertan el journal del sistema, para verlos ejecutar:
            journalctl CONTAINER_NAME=opendata-crawler -f
