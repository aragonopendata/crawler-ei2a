#!/bin/sh
# From https://www.digitalocean.com/community/tutorials/how-to-install-and-use-docker-on-ubuntu-16-04

if [ -e "$BASH" ] ;then echo  ${txtbld}$(tput setaf 1) Please run this script $0 with sh $(tput sgr0)  ; exit 1; fi

check(){

  if [ $1 -ne 0  ] ;then echo ${txtbld}$(tput setaf 1)  error in execution $(tput sgr0)  ; exit 1; fi
}


curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
check $?

add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"
check $?

apt-get update
check $?

apt-cache policy docker-ce
check $?

apt-get install -y docker-ce
check $?

systemctl status docker
check $?

#If you want to avoid typing sudo whenever you run the docker command, add your username to the docker group:
#usermod -aG docker $(id ubuntu -u)
#check $?