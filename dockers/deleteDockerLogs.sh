#!/bin/bash -e

question(){
  question=$1
  action=$2

  read -p "$question (y/n) " answer
  case ${answer} in
    y )
        $action
    ;;
    * )
        echo No
    ;;
  esac
}

truncateFile() {
  log=$1
  sudo truncate -s 0 $log
  echo "After truncation Log file info:  $(sudo ls -lat $log)"
}


echo "Deletes logs (console logs) of specified docker. eg:"
echo "      deleteDockerLogs argon-jetty"

if [[ -z $1 ]]; then
    echo "No container specified"
    exit 1
fi

if [[ "$(sudo docker ps -aq -f name=^/${1}$ 2> /dev/null)" == "" ]]; then
    echo "Container \"$1\" does not exist, exiting."
    exit 1
else
    echo "Looking for logPath of container $1:"
fi

log=$(sudo docker inspect -f '{{.LogPath}}' $1 2> /dev/null)
echo "Current Log file info:  $(sudo ls -lat $log)"
question "Do you want to truncate file $log?" "truncateFile $log"
