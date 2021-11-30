#!/usr/bin/env bash

docker network create -d bridge --subnet 192.168.102.0/24 --gateway 192.168.102.1 argon-net