#!/bin/bash
if [ -e "$SH" ] ;then echo  ${txtbld}$(tput setaf 1) Please run this script $0 with bash $(tput sgr0)  ; exit 1; fi


envName=$1
# pythonVersion=$2

FOLDER_CONDA_ENVS=/opt/conda/envs

cd $FOLDER_CONDA_ENVS
echo Installing Conda Environment $envName
# with python version $pythonVersion...
echo Removing env $envName...
if ! conda-env remove -y -n $envName; then
	echo "Warning removing env. let's continue anyway"
fi

lstFile=$FOLDER_CONDA_ENVS/listOfLibrariesForEnv_$envName.yml

sed -i '/es-core-\|en-core-/d'  $lstFile
echo Creating new env $envName with libraries listed in $lstFile file...
if ! conda-env create --force -n $envName -f  $lstFile; then
	echo Error creating conda env $envName!. Review file $lstFile!
	exit
fi

echo Created env $envName!

# not necessary as the file has the python version --> python=$pythonVersion
source activate $envName
KERNEL_NAME=kernel_$envName
echo Creating Jupyterhub kernel $KERNEL_NAME...
pip install ipykernel
python -m ipykernel install --user --name $KERNEL_NAME --display-name  "Kernel based on Conda Env $envName"
#  (Python $pythonVersion)"
