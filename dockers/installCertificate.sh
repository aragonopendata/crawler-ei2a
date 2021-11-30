#!/bin/sh
# From https://www.digitalocean.com/community/tutorials/how-to-install-and-use-docker-on-ubuntu-16-04

if [ -e "$BASH" ] ;then echo  ${txtbld}$(tput setaf 1) Please run this script $0 with sh $(tput sgr0)  ; exit 1; fi

check(){

  if [ $1 -ne 0  ] ;then echo ${txtbld}$(tput setaf 1)  error in execution $(tput sgr0)  ; exit 1; fi
}

sudo mkdir /usr/local/share/ca-certificates/docker-dev-cert
check $?

cp ../certificate/devdockerCA.crt /usr/local/share/ca-certificates/docker-dev-cert/devdockerCA.crt
check $?

sudo update-ca-certificates
check $?

sudo service docker restart
check $?
