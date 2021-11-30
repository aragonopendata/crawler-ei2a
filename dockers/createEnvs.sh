#!/bin/bash

for entry in ../envs/*
do
  echo $entry
  sinpaths=${entry##*/}
  cp ../envs/$entry /argon/envs/listOfLibrariesForEnv_${sinpaths%.*}.yml
  chown :mstudio  /argon/envs -R
  chmod 0777  /argon/envs -R
  sudo docker exec -it argon-jupyterhub /opt/conda/envs/dockerCreateCondaEnvAndJupyterKernel.sh  ${sinpaths%.*}

done


