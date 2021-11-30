#!/bin/bash


if [ "$#" -ne 1 ]; then
    echo "Expected file with a list of notebook paths (1 per line)"
    exit
fi

echo Running notebooks found on file $1...

REST_API_CREATENOTEBOOK='http://argon-containermanager:9999/cm/v1/notebooks/create'
#REST_API_CREATENOTEBOOK='http://localhost:8891/cm/v1/notebooks/create'
CURL_HOST=argon-jetty
LINES=$(cat $1 | tr -d '\r')
arr=( $LINES )
echo
for i in "${arr[@]}"; do
echo "Running notebook $i..."
export JSON=$(cat << EOF
{"path":"$i"}
EOF
)
        # echo $JSON

        # CMD=$(cat << EOF
        # curl -X POST --header 'Content-Type:application/json' -d '{"path":"$i"}' 'http://localhost:8891/cm/v1/notebooks/create'
        # EOF
        # )

        CMD=$(cat << EOF
sudo docker exec $CURL_HOST bash -c "curl -X POST --header 'Content-Type:application/json' -d '{\"path\":\"$i\"}' '$REST_API_CREATENOTEBOOK'"
EOF
)

        echo $CMD
        eval "$CMD"
        # ST=$?
        echo
        # if [ $ST -eq 0 ]; then
        #  echo "Notebook Gateway $i started!"
        # else
        #  echo "ERROR: Notebook Gateway $i launched an error when starting: $ST"
        # fi
done

