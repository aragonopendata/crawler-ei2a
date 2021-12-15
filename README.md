# crawler-ei2a

Este proyecto contiene las carpetas y archivos necesarios para desplegar la aplicación que realiza el rastreo de las páginas web y pdfs de ciertos portales del Gobierno de Aragón e introduce los datos obtenidos dentro del gráfo de la ontología  https://opendata.aragon.es/def/ei2av2/

## Requisitos

Las librerias usadas en este proyecto y sus respectivas versiones se pueden ver en el archivo 'src/main/python/requirements.txt'.

## Estructura de carpetas

- src/main/docker : archivos de configuración de la imagen de docker

- src/main/python: codigo fuente del crawler

- src/main/script : script para generar la imagen de docker y ejecutar el crawler dentro de la imagen. 

## Configuración 

El archivo  'src/main/python/config.py' contiene los parámetros de configuración

```
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

sparql_user=***

#contraseña del servidor de sparql

sparql_pass=***

#url del servidor de sparql

sparql_server=***

#path donde se encuentra el servicio de queries GET, sin autenticacion

sparql_path='/sparql'

#path donde se encuentra el servicio de queries POST, con autenticacion

sparql_path_auth='/sparql-auth'
```
El parámetro de configuración __urls__ se usa en caso de que el parametro __urlsfile__ no este configurado o el fichero especificado en el no exista. 

## Fichero de urls
El archivo __urls.csv__ que esta asignado en el parámetro de configuración __urlsfile__ contiene una tabla en formato csv con dos columnas que son la url a procesar y el sector o categoría en que se clasifica, el contenido que tiene actualmente es el siguiente:
```
url,sector
https://transparencia.aragon.es,sector-publico
https://www.saludinforma.es,salud
https://educa.aragon.es/,educacion
https://www.turismodearagon.com/es/,turismo
https://acpua.aragon.es/,educacion
https://arasaac.org/,sociedad-bienestar
http://patrimonioculturaldearagon.es/,cultura-ocio
http://www.sarga.es,medio-ambiente
https://inaem.aragon.es/,empleo
https://sda.aragon.es/,ciencia-tecnologia
https://aragoncircular.es/,economia
http://www.aragonhoy.net/,sector-publico
```

## Instalación y paso entre entornos 

Para instalar el crawler simplemente hay que clonar el repositorio en la máquina correspondiente y rellenar los valores del fichero de configuración anteriror que tienen '***' con los valores adecuados en cada entorno.

Antes de ejecutar el programa se debe crear la imagen de docker que contiene dicho programa y todas sus dependencias, para ello hay que ejecutar el siguente comando desde la carpeta principal del proyecto
```sh
sh src/main/script/build.sh
```
Una vez creada la imagen para lanzar la ejecución del programa se ejecutará: 
```sh
sh src/main/script/run.sh
 ``` 
Cuando el programa haya procesado todas la urls que haya encontrado y que esten dentro de los dominios configurados el contenedor docker desaparece.


## Ejecución periódica

Se debe configurar el ejecución periodica del crawler en cron u otro sistema similar. Se recomienda que la frecuencia de ejecucion sea semanal o mensual. 

La siguiente línea configura cron para lanzar la tarea a las 00:00 de cada domingo, el proyecto se ha clonado en /argon/work/opendata-crawler/
```cron
0 0 * * 0  sh /argon/work/opendata-crawler/src/main/script/run.sh
```

## LOG 

Los mensajes de log se insertan el journal del sistema, para verlos ejecutar:
```
journalctl CONTAINER_NAME=opendata-crawler -f
```
