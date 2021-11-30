#/bin/bash
sudo docker volume create --name argon-jupyter_notebooks --driver local-persist  --opt mountpoint=/argon/notebooks/work

sudo docker volume create --name argon-jupyter_notebooks_data --driver local-persist  --opt mountpoint=/argon/notebooks/work/data

sudo docker volume create --name argon-jupyter_envs --driver local-persist  --opt mountpoint=/argon/envs

sudo docker volume create --name argon-logs --driver local-persist  --opt mountpoint=/argon/logs

sudo docker volume create --name argon-logs_gateways --driver local-persist  --opt mountpoint=/argon/logs/gateways

sudo docker volume create --name argon-data --driver local-persist  --opt mountpoint=/argon/data/

sudo docker volume create --name argon-dump --driver local-persist  --opt mountpoint=/argon/dump/

sudo docker volume create --name argon-wars --driver local-persist  --opt mountpoint=/argon/war/

sudo docker volume create --name argon-conf --driver local-persist  --opt mountpoint=/argon/conf

sudo docker volume create --name argon-nodejs --driver local-persist  --opt mountpoint=/argon/nodejs


