crawler-ei2a

Este proyecto contiene las carpetas y archivos necesarios para desplegar la aplicación que realiza el rastreo de ciertos portales del Gobierno de Aragón

Para realizar la instalación de la aplicación se necesitan las siguientes carpetas:
- 	certificate : contiene el certificado digital para conectarse al repositorio docker de itainnova 
- 	conf: archivos de configuración
- 	cronScripts: scripts que lanzan los crawlers desde cron ( sudo crontab –e)
- 	docker: script de docker-compose para la instalción del sistema
- 	dockers: scripts para instalar y actualizar los dockers
- 	envs: carpeta que contiene los entornos de python y los script para crearlos
- 	lib: actualizaciones de librerias de Moriarty usadas en este proyecto
- 	mongo: datos para inicializar las coleciones de mongoDB usadas por Moriarty
- 	notebooks: carpeta con los datos y los notebooks de jupyter
- 	solr: configuracion de la base de datos de  solr.
- 	war: carpeta que contienen las aplicaciones web que se despliegan.
