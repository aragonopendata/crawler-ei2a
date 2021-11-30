#!/bin/bash
if [ -e "$SH" ] ;then echo  ${txtbld}$(tput setaf 1) Please run this script $0 with bash $(tput sgr0)  ; exit 1; fi

createCondaEnv() {
envName=$1
pythonVersion=$2
echo Installing Conda Environment $envName with python version $pythonVersion and Jupyter Kernel matching this environment...
CMD="/opt/conda/envs/dockerCreateCondaEnvAndJupyterKernel.sh $envName $pythonVersion"
sudo docker exec -it argon-jupyterhub $CMD
}



question(){
read -p "Do you want install ${txtbld}$(tput setaf 1)  $1 service $(tput sgr0) (y/n) ? " answer
case ${answer} in
    y )
        $2
    ;;
    * )
        echo No
    ;;
esac


}

createCondaEnv "py36" "3.6"
question "Do you want to create a python 2.7 Conda env?" "createCondaEnv py27 2.7"


