#!/usr/bin/env bash
echo "------------------------------------------"
echo "Crear directorios"
echo "------------------------------------------"

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
mkdir -p /argon/data/solr/opendata/data
mkdir -p /argon/data/virtuoso

sh ./dockers/createVolumes.sh
sh ./dockers/createNetwork.sh

echo "------------------------------------------"
echo "Copiar la configuracion"
echo "------------------------------------------"

cp ./conf /argon/ -r
cp ./solr/* /argon/data/solr -r

echo "------------------------------------------"
echo "Copiar las webs "
echo "------------------------------------------"
cp ./war/* /argon/war/ -r

echo "------------------------------------------"
echo "Copiamos los notebooks"
echo "------------------------------------------"
cp  ./notebooks/* /argon/notebooks/work -r

echo "------------------------------------------"
echo "Copiamos los script de cron"
echo "------------------------------------------"
cp  ./cronScripts/* /argon/cronScripts -r

echo "------------------------------------------"
echo "Dar la propiedad de la jerarquía de carpetas creadas al grupo de usuarios de mstudio"
echo "------------------------------------------"




chown :mstudio  /argon/war -R
chown :mstudio  /argon/notebooks -R
chown :mstudio  /argon/work -R
chown :mstudio  /argon/crontab -R 
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
chmod  0774 /argon/cronScripts -R


echo "------------------------------------------"
echo "Descargamos las librerias de moriarty en /argon/conf/m3restapi"
echo "------------------------------------------"
docker run --rm --name argon-repository -it --entrypoint 'cp' -v /argon/conf/m3restapi:/tmp argon-docker.itainnova.es/v2/argon/m3repository:latest /m2 /tmp -R
chmod  0774 /argon/conf/m3restapi -R
chown :mstudio  /argon/conf -R

echo "------------------------------------------"
echo " Instalar los contenedores con los modulos"
echo "------------------------------------------"
cd docker
docker-compose  -f  docker-compose.yml up -d

echo "------------------------------------------"
echo " Configuramos el acceso externo "
echo "------------------------------------------"

sh -c " . ./configureKongV2.sh && configureKong"
cd ..

echo "------------------------------------------"
echo " Restauramos la base de datos de moriarty"
echo "------------------------------------------"
cp mongo/* /argon/dump/ -r
sudo docker exec argon-mongo mongoimport --drop --mode upsert  --db moriarty --collection wf --file /tmp/dump/moriarty/wf.json
sudo docker exec argon-mongo mongoimport --drop --mode upsert  --db moriarty --collection category --file /tmp/dump/moriarty/category.json
sudo docker exec argon-mongo mongoimport --drop --mode upsert  --db moriarty --collection style --file /tmp/dump/moriarty/style.json
sudo docker exec argon-mongo mongoimport --drop --mode upsert  --db moriarty --collection dashboard --file /tmp/dump/moriarty/dashboard.json
sudo docker exec argon-mongo mongoimport --drop --mode upsert  --db moriarty --collection dashcategory --file /tmp/dump/moriarty/dashcategory.json

echo "------------------------------------------"
echo "Crear los entornos"
echo "------------------------------------------"
cp  ./envs/* /argon/envs/ -r
cd dockers
cp dockerCreateCondaEnvAndJupyterKernel.sh /argon/envs/
cp createCondaEnvsAndJupyterKernels.sh /argon/envs/
sh createEnvs.sh

echo "------------------------------------------"
echo " Iniciar los notebooks con servicio"
echo "------------------------------------------"
sh runListOfNotebooks.sh  listRunningNotebooks.lst


echo "------------------------------------------"
echo "Cargar la ontologia"
echo "------------------------------------------"


docker exec argon-jetty bash -c "wget https://opendata.aragon.es/def/ei2a/ei2a.owl"
docker exec argon-jetty bash -c "curl --digest --user dba:dba --verbose --url \"http://argon-virtuoso:8890/sparql-graph-crud-auth?graph-uri=http://opendata.aragon.es/def/ei2a\" -X POST -T ei2a.owl" 
docker exec argon-jetty bash -c "rm ei2a.owl"
docker exec argon-jetty bash -c "wget https://opendata.aragon.es/def/ei2a/categorization.owl"
docker exec argon-jetty bash -c "curl --digest --user dba:dba --verbose --url \"http://argon-virtuoso:8890/sparql-graph-crud-auth?graph-uri=http://opendata.aragon.es/def/ei2a/categorization\" -X POST -T categorization.owl"
docker exec argon-jetty bash -c "rm categorization.owl" 