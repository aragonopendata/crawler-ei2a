#!/bin/sh
# From https://www.digitalocean.com/community/tutorials/how-to-install-and-use-docker-on-ubuntu-16-04

check(){

  if [ $1 -ne 0  ] ;then echo ${txtbld}$(tput setaf 1)  error in execution $(tput sgr0)  ; exit 1; fi
}

sudo yum install -y yum-utils device-mapper-persistent-data lvm2
check $?

sudo yum-config-manager --add-repo  https://download.docker.com/linux/centos/docker-ce.repo
check $?

sudo yum makecache fast
check $?

sudo subscription-manager repos --enable=rhel-7-server-extras-rpms
check $?

sudo yum -y install container-selinux
check $?

sudo yum -y install docker-ce
check $?

sudo systemctl start docker
check $?

systemctl status docker
check $?
