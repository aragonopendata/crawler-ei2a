#!/bin/bash
#python3 /argon/cronScripts/DownloadCSVs.py
docker exec -it argon-jupyterhub python3 /home/jovyan/work/DownloadCSVs.py
curl http://localhost:8889/web-server/rest/executeWorkFlowGet/5ad9aba6b8b29400084a9004


