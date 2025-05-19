#!/bin/bash

# Nombre del contenedor
CONTAINER_NAME="opendata-crawler"

# Verifica si el contenedor está en ejecución
if [ "$(docker ps -q -f name=$CONTAINER_NAME)" ]; then
    echo "Deteniendo y eliminando el contenedor en ejecución: $CONTAINER_NAME"
    docker stop $CONTAINER_NAME && docker rm $CONTAINER_NAME
elif [ "$(docker ps -aq -f name=$CONTAINER_NAME)" ]; then
    echo "Eliminando contenedor detenido: $CONTAINER_NAME"
    docker rm $CONTAINER_NAME
fi

# Ejecuta el contenedor
echo "Iniciando nuevo contenedor: $CONTAINER_NAME"
docker run --rm --name=$CONTAINER_NAME --privileged -d opendata-crawler:1.0.0
