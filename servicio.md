#  Pasos previos para instalar:

## Clonar el proyecto



## Crear el grupo mstudio
Si el grupo con gid=180730 no existe en la máquina host, este ha de ser creado con el siguiente comando (mstudio es el nombre usado). Si dicho gid estuviera asignado a otro grupo, los siguientes comandos deberían sustituir mstudio por el nombre del grupo con dicho gid.
```bash
sudo groupadd mstudio –g 180730
```
## Si no funciona el comando, seguir los siguientes pasos:
Crear el grupo sin el gid (-g 180730)

```bash
sudo groupadd mstudio
```
Editar el fichero /etc/group

```bash
sudo vi /etc/group
```
Sustituir la descripción del grupo mstudio que sigue la sintaxis mstudio:x:<gid>: por la descrición que asocia al grupo mstudio con el gid 180730:

```bash
mstudio:x:180730:
```
Salvar el fichero y salir del editor

## Modificar el fichero /etc/hosts
Añadir el siguiente texto debajo de la IP 127.0.0.1 (Introducir las confguracion de docker-registry de ITAInnova)

```bash
docker-registry_ITAINNOVA1 
docker-registry_ITAINNOVA2  a
```
## Instalar docker
```bash
sh ./dockers/installDocker.sh
```

## Configurar docker
```bash
sudo vi /lib/systemd/system/docker.service
```
Sustituir la linea que empieza con ExecStart por:   
```bash
ExecStart=/usr/bin/dockerd  -H unix://  -H=tcp://0.0.0.0:2375  -g=/argon/docker-data $DOCKER_OPTS
```
Guardar cambios y reiniciar docker
```bash
sudo systemctl daemon-reload
sudo service docker restart
```

## Instalar los certificados 

Copiar los certificados que haya proporcionado ITAInnova

```bash
sudo  mkdir  /usr/local/share/ca-certificates/docker-dev-cert –p
sudo cp certificate/devdockerCA.crt /usr/local/share/ca-certificates/docker-dev-cert/devdockerCA.crt

sudo update-ca-certificates
sudo service docker restart
mkdir /root/.docker
cp certificate/config.json  /root/.docker/
sudo service docker restart
```
## Instalar docker compose  

```bash
$ sudo curl -L https://github.com/docker/compose/releases/download/1.27.4/docker-compose-Linux-x86_64 -o /usr/local/bin/docker-compose && sudo chmod +x /usr/local/bin/docker-compose
```


# Instalación de los contenedores y datos propios del proyecto

## Editar el archivo docker/env.yml 
Establecer las siguientes variables de entorno con la ip de la máquina

```bash 
argonMoriartyPublicIP=
dockerServer=
```

## Los siguientes pasos se pueden ejecutar con script install.sh
```bash
sh install.sh
```

## Crear las carpetas argon y datos
```bash
mkdir -p /argon
mkdir -p /argon/war/
mkdir -p /argon/notebooks
mkdir -p /argon/notebooks/work
mkdir -p /argon/notebooks/work/data
mkdir -p /argon/work
mkdir -p /argon/crontab
mkdir -p /argon/envs
mkdir -p /argon/logs
mkdir -p /argon/logs/gateways
mkdir -p /argon/logs/solr
mkdir -p /argon/logs/moriarty
mkdir -p /argon/logs/argonWebApp
mkdir -p /tmp
mkdir -p /argon/dump
mkdir -p /argon/cronScripts

mkdir -p /argon/data/mongo
mkdir -p /argon/data/solr
mkdir -p /argon/data/solr/webaragon/data
mkdir -p /argon/data/solr/opendata/data
mkdir -p /argon/data/virtuoso

sh ./dockers/createVolumes.sh
sh ./dockers/createNetwork.sh

```
## Crear los volumenes y las red interna
```bash
sh ./dockers/createVolumes.sh
sh ./dockers/createNetwork.sh
```
## Recarga docker daemon
```bash
$ sudo systemctl daemon-reload
```
## Reiniciar el contenedor
```
$ sudo service docker restart
```

## Copiar la configuracion
```bash
cp ./conf /argon/ -r
cp ./solr/* /argon/data/solr -r
```
## Copiar la web de visualizacion 
```bash
cp ./war/opendata /argon/war -r
```

## Copiar los notebooks
```bash
cp  ./notebooks/* /argon/notebooks/work -r
```

## Copiar los script de cron
```bash
cp  ./cronscripts/* /argon/cronScripts -r
```

## Dar la propiedad de la jerarquía de carpetas creadas al grupo de usuarios de mstudio
```bash


chown :mstudio  /argon/war -R
chown :mstudio  /argon/notebooks -R
chown :mstudio  /argon/work
chown :mstudio  /argon/crontab 
chown :mstudio  /argon/envs -R
chown :mstudio  /argon/logs -R
chown :mstudio  /argon/dump -R
chown :mstudio  /argon/data -R
chown :mstudio  /argon/conf -R


chmod  0774  /argon/war  -R
chmod  0774  /argon/notebooks -R
chmod  0774  /argon/work -R
chmod  0774  /argon/crontab -R
chmod  0774  /argon/envs -R
chmod  0774  /argon/logs -R
chmod  0774  /argon/dump -R
chmod  0774  /argon/data -R
chmod  0774  /argon/conf -R
```
## Descargamos las librerias de moriarty en /argon/conf/m3restapi
```bash
docker run --rm --name argon-repository -it --entrypoint 'cp' -v /argon/conf/m3restapi:/tmp argon-docker.itainnova.es/v2/argon/m3repository:latest /m2 /tmp -R
chown :mstudio  /argon/conf/m3restapi

chmod  0774 /argon/conf/m3restapi -R
chown :mstudio  /argon/conf -R

```
## Instalar los contenedores con los modulos
```bash
cd docker
docker-compose  -f  docker-compose.yml up -d
```
## Configurar el acceso externo
```bash
sh -c " . ./configureKongV2.sh && configureKong"
cd ..
```
## Restaurar la base de datos de moriarty
```bash
cp mongo/* /argon/dump/ -r
sudo docker exec argon-mongo mongoimport --drop --mode upsert  --db moriarty --collection wf --file /tmp/dump/moriarty/wf.json
sudo docker exec argon-mongo mongoimport --drop --mode upsert  --db moriarty --collection category --file /tmp/dump/moriarty/category.json
sudo docker exec argon-mongo mongoimport --drop --mode upsert  --db moriarty --collection style --file /tmp/dump/moriarty/style.json
sudo docker exec argon-mongo mongoimport --drop --mode upsert  --db moriarty --collection dashboard --file /tmp/dump/moriarty/dashboard.json
sudo docker exec argon-mongo mongoimport --drop --mode upsert  --db moriarty --collection dashcategory --file /tmp/dump/moriarty/dashcategory.json
```

## Crear los entornos
```bash
cp  ./envs/* /argon/envs/ -r
cd dockers
cp dockerCreateCondaEnvAndJupyterKernel.sh /argon/envs/
cp createCondaEnvsAndJupyterKernels.sh /argon/envs/
sh createEnvs.sh
```


## Iniciar los notebooks con servicio
```bash
sh runListOfNotebooks.sh  listRunningNotebooks.lst
```

## Cargar la ontologia

```bash
docker exec argon-jetty bash -c "wget https://opendata.aragon.es/def/ei2a/ei2a.owl"
docker exec argon-jetty bash -c "curl --digest --user dba:dba --verbose --url \"http://argon-virtuoso:8890/sparql-graph-crud-auth?graph-uri=http://opendata.aragon.es/def/ei2a\" -X POST -T ei2a.owl" 
docker exec argon-jetty bash -c "rm ei2a.owl"
docker exec argon-jetty bash -c "wget https://opendata.aragon.es/def/ei2a/categorization.owl"
docker exec argon-jetty bash -c "curl --digest --user dba:dba --verbose --url \"http://argon-virtuoso:8890/sparql-graph-crud-auth?graph-uri=http://opendata.aragon.es/def/ei2a/categorization\" -X POST -T categorization.owl"
docker exec argon-jetty bash -c "rm categorization.owl" 
```
# Configurar cron

crontab -e

0 0 * * * /argon/cronScripts/launchWF.sh &>/dev/null
9 4  * * * /argon/cronScripts/loadCSVs.sh &>/argon/logs/loadCSVs.log


