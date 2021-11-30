#!/bin/sh

URL_KONG=http://localhost:8888
AUTH_METHOD=basic-auth
ALL_VERBS="[\"GET\", \"POST\", \"DELETE\", \"PUT\", \"HEAD\", \"CONNECT\", \"OPTIONS\", \"TRACE\", \"FETCH\", \"PATCH\"]"
DEBUG=1

########################################
### GLOBAL VARIABLES                 ###
########################################
#SERVICE_ID will contain the id of the services created by method createService
SERVICE_ID=
#ROUTE_ID will contain the id of the route created by method addRoute2Service
ROUTE_ID=
NTOTAL=0


########################################
### SECTION UTILITY METHODS  (BEGIN) ###
########################################
printHelp() {
      echo "Usage:"
      echo "    sh -c \". ./configureKongV2.sh && getServices\"                             Prints out info about the installed services (and their routes)"
      echo "    sh -c \". ./configureKongV2.sh && deleteKongItem services <serviceName>\"   Deletes a service and its routes"
      echo "    sh -c \". ./configureKongV2.sh && <methodName>\"        			  Executes the method specified:"
      echo "    ... Where <methodName> can be one of these: configureArgonWA, configureContainerManager, configureJetty, configureM3"
      echo "          , configureNodejs, configureMongoViewer, configureCloudera, configureJupyter, configureSolr, configureVirtuoso"
      echo "          **configureKong** or any other custom configuration method defined in inherited scripts"
      echo "--------------------------------"
      echo ""
}



####################################
## Methods to work over arrays BEGIN
####################################
getItemFromStringAsArray() {
  STR_ARRAY=$1
  SEPARATOR=$2
  if test -n "$3"; then
    INDEX=$3
  else
    INDEX=0
  fi



  N=0
#  echo "getItemFromString $STR_ARRAY $SEPARATOR $INDEX $N..."
  echo $STR_ARRAY | tr ${SEPARATOR} \\n | while read ID ; do
#       echo "Trying $N ID=$ID..."
        if [ "$N" -eq "$INDEX" ]; then
#            echo "Found! $ID"
            echo $ID
            return
        fi
        N=$(( $N + 1 ))
   done
}


getLengthOfStringAsArray() {
  STR_ARRAY=$1
  SEPARATOR=$2
  echo $(echo $STR_ARRAY | tr ${SEPARATOR} \\n | wc -l)
}
####################################
## Methods to work over arrays END
####################################


## getRoutes: Given a service name, prints out routes
getRoutes() {
   ITEM="services"
   NAME=$1
   CMD=$(echo "curl -s -X GET $URL_KONG/$ITEM/$NAME/routes")
   ROUTE_IDS1_RESPONSE=$(eval $CMD)
   IS_HERE=$(echo $ROUTE_IDS1_RESPONSE | grep "Not found" | wc | awk '{print $2}')
   if [ "$IS_HERE" -ne "0" ]; then
     echo "$GAP No routes found for $ITEM with name $NAME"
     return
   fi
   ROUTE_IDS=$(echo $ROUTE_IDS1_RESPONSE \
                | python3 -c "exec(\"import sys, json; xs=json.load(sys.stdin)['data'];\nfor x in xs: print('{};'.format(x['id']))\")")
   ROUTE_PATHS=$(echo $ROUTE_IDS1_RESPONSE \
                | python3 -c "exec(\"import sys, json; xs=json.load(sys.stdin)['data'];\nfor x in xs: print('{};'.format(x['paths']))\")")
   ROUTE_METHODS=$(echo $ROUTE_IDS1_RESPONSE \
                | python3 -c "exec(\"import sys, json; xs=json.load(sys.stdin)['data'];\nfor x in xs: print('{};'.format(x['methods']))\")")
   ROUTE_PROTOCOLS=$(echo $ROUTE_IDS1_RESPONSE \
                | python3 -c "exec(\"import sys, json; xs=json.load(sys.stdin)['data'];\nfor x in xs: print('{};'.format(x['protocols']))\")")
   ROUTE_PRESERVE=$(echo $ROUTE_IDS1_RESPONSE \
                | python3 -c "exec(\"import sys, json; xs=json.load(sys.stdin)['data'];\nfor x in xs: print('{};'.format(x['preserve_host']))\")")

   RLENGTH=${#ROUTE_PATHS}
   if [ "$RLENGTH" -eq "0" ]; then
     echo "$GAP No routes found for $ITEM with name $NAME"
     return
   else
     NTOTAL=$(getLengthOfStringAsArray "$ROUTE_IDS" ";")
     XGAP=$GAP
     GAP="$GAP  "
     echo "$GAP Routes ($NTOTAL):"
     GAP="$GAP  "
     i=0
     echo $ROUTE_PATHS | tr \; \\n | while read PATHS ; do \
	if test -n "$PATHS"; then
		RID=$(getItemFromStringAsArray "$ROUTE_IDS" ";" $i)
                RMETHODS=$(getItemFromStringAsArray "$ROUTE_METHODS" ";" $i)
                RPROTOCOLS=$(getItemFromStringAsArray "$ROUTE_PROTOCOLS" ";" $i)
		RPRESERVE=$(getItemFromStringAsArray "$ROUTE_PRESERVE" ";" $i)

	        echo "$GAP - ROUTE $i WITH PATHS $PATHS and ID $RID"
	        echo "$GAP        AND METHODS $RMETHODS"
		echo "$GAP      AND PROTOCOLS $RPROTOCOLS"
		echo "$GAP  AND PRESERVE HOST $RPRESERVE"
        	i=$(( $i + 1 )) 
	else
		echo "$GAP - ROUTE $i HAS NO PATHS"
	fi
	echo
     done
     GAP=$XGAP
   fi
}


getService() {
  ID=$1
  CMD=$(echo "curl -s -X GET $URL_KONG/services")
  RESPONSE=$(eval $CMD)
  SERVICE_IDS=$(echo $RESPONSE \
         | python3 -c "exec(\"import sys, json; xs=json.load(sys.stdin)['data'];\nfor x in xs: print('{};'.format(x['id']))\")")

  if test -n "$ID";
          then
                  RESULT=$(getItemFromStringAsArray "$SERVICE_IDS" ";" $iS)
                  echo "$GAP $iS- Service $ID(${RESULT})"
                  GAP="$GAP  "
                  getRoutes $ID
                  iS=$(( $iS + 1 ))
                  GAP=$XGAPS
          fi
}


##getServices: Prints out info about all services
getServices() {
	CMD=$(echo "curl -s -X GET $URL_KONG/services")
	RESPONSE=$(eval $CMD)
	SERVICE_NAMES=$(echo $RESPONSE \
                | python3 -c "exec(\"import sys, json; xs=json.load(sys.stdin)['data'];\nfor x in xs: print('{};'.format(x['name']))\")")

	RLENGTH=${#SERVICE_NAMES}

	NSERVICES=$(getLengthOfStringAsArray "$SERVICE_NAMES" ";")
	echo "> Service Names ($NSERVICES)"
	iS=0
	XGAPS=$GAP

	echo ${SERVICE_NAMES} | tr \; \\n | while read ID ; do 
		getService $ID
	done
}

deleteKongItem() {
  ITEM=$1
  NAME=$2
  GAP=$3
  echo "$GAP Deleting $ITEM with name $NAME..."
  GAP="$GAP  "

  if [ $ITEM = "services" ];
  then
   CMD=$(echo "curl -s -X GET $URL_KONG/$ITEM/$NAME/routes")
      if [ "$DEBUG" -eq "1" ]; then
        echo "$GAP Looking for routes on $ITEM $NAME..."
        echo "$GAP>$CMD"
      fi
   ROUTE_IDS1_RESPONSE=$(eval $CMD)
   IS_HERE=$(echo $ROUTE_IDS1_RESPONSE | grep "Not found" | wc | awk '{print $2}')
   if [ "$IS_HERE" -ne "0" ]; then
     echo "$GAP No routes found for $ITEM with name $NAME"
   fi

   ROUTE_IDS1_LIST=$(echo $ROUTE_IDS1_RESPONSE \
                | python3 -c "exec(\"import sys, json; xs=json.load(sys.stdin)['data'];\nfor x in xs: print('{};'.format(x['id']))\")")
   RLENGTH=${#ROUTE_IDS1_LIST}

  
   if [ "$RLENGTH" -eq "0" ]; then
     echo "$GAP No routes found for $ITEM with name $NAME"
   else
     echo $ROUTE_IDS1_LIST | tr \; \\n | while read ID ; do \
          RLENGTH=${#ID}
          if [ "$RLENGTH" -ne "0" ]; then
            NAME1=$NAME
            GAP1=$GAP
            ITEM1=$ITEM
            deleteKongItem "routes" $ID "$GAP  "
            GAP=$GAP1
            NAME=$NAME1
            ITEM=$ITEM1
          fi
     done
   fi 
  fi

  # echo "Checking if item $1 with name $2 exists..."
  CHK=$(curl -s -X GET $URL_KONG/$ITEM/$NAME)
  IS_HERE=$(echo $CHK | grep "Not found" | wc | awk '{print $2}')
  if [ "$IS_HERE" -eq "0" ];
  then
    ITEM_ID1=$(curl -s -X GET $URL_KONG/$ITEM/$NAME | python3 -c "import sys, json; print(json.load(sys.stdin)['id'])")

    IS_HERE=$(echo $1 | wc | awk '{print $2}')
    if [ "$IS_HERE" -eq "0" ]; then 
      echo "$GAP No $ITEM with name $NAME";
    else
      echo "$GAP Destroying $ITEM with name $NAME...";
      CMD=$(echo "curl -s -X DELETE $URL_KONG/$ITEM/$NAME")
      if [ "$DEBUG" -eq "1" ]; then
        echo "$GAP>Delete $ITEM: $CMD"
      fi
      eval $CMD
    fi
  else
    echo "$GAP No $ITEM with given name $NAME";
  fi
}

createUser() {
  deleteKongItem "consumers" $1
  echo "Adding user $1..."
  X=$(echo "\"username=$1&custom_id=$1\"")
  X=$(echo "curl -s -X POST -d $X $URL_KONG/consumers/")
  eval $X

  echo Adding $AUTH_METHOD to user user...
  X=$(echo "\"password=$2\"")
  echo "X=$X"
  X1=$(echo "\"username=$1\"")
  echo "X1=$X1"
  X2=$(echo "curl -s -X POST $URL_KONG/consumers/$1/$AUTH_METHOD --data $X1 --data $X")
  eval $X2
}

addSecurityToRoute() {
 echo " Adding $AUTH_METHOD Auth to route $1..."
 X=$(echo "\"name=$AUTH_METHOD\"")
 X=$(echo "curl -s -X POST \
  $URL_KONG/routes/$1/plugins \
   --data $X \
   --data \"config.hide_credentials=false\"")
 AUTH_PLUGIN=$(eval $X | python3 -c "import sys, json; print(json.load(sys.stdin)['id'])")
}

addFileLog() { 
  X=$(echo "curl -X POST $URL_KONG/services/$1/plugins --data \"name=file-log\" --data \"config.path=$2\"")
  AUTH_PLUGIN=$(eval $X | python3 -c "import sys, json; print(json.load(sys.stdin)['id'])")
}

addCertificate() {
  CERT_NAME=$1
  deleteKongItem "certificates" $2
  N=$'\n'
  ID=$(echo "\"id\":\"$1\"")
  C=$(echo "\"cert\":\"$(cat $3)\"")

  K=$(echo "\"key\":\"$(cat $4)\"")

  S=$(echo "\"snis\":[\"$2\"]")
  #J=$(echo "{$ID, $C, $K, $S}")
  J=$(echo "{ $ID, $C, $K, $S}")
  CMD=$(echo "curl -s -X POST -H 'Content-Type: application/json' \
    $URL_KONG/certificates/ -d '$J'")
  echo "CMD=$CMD"
  eval $CMD
}

modifyRequestRemoveAddHeaders() {
 echo "  Removing Host headers \"$2\" to requests to $1..."
 echo "  Adding Host headers \"$3\" to requests to $1..."

 X=$(echo "curl -X POST
 $URL_KONG/routes/$1/plugins
    --data 'name=request-transformer'
    --data 'config.remove.headers=$2'
    --data 'config.add.headers=$3'")
 echo $X
 eval $X
}

modifyRequestChangeHttpMethod() {
 echo "Changing http method to $2"

 X=$(echo "curl -X POST
 $URL_KONG/routes/$1/plugins
    --data 'name=request-transformer'
    --data 'config.http_method=$2'")
 echo $X
 eval $X
}

addFileLog() {
 echo "Adding file log $2 to $1"
 X=$(echo "curl -X POST $URL_KONG/services/$1/plugins \
    --data \"name=file-log\" \
    --data \"config.path=$2\"")
 echo $X

 AUTH_PLUGIN=$(eval $X | python3 -c "import sys, json; print(json.load(sys.stdin)['id'])")
}

createService() {
 SERVICE_NAME=$1
 SERVICE_URL=$2
 echo "** ADDING SERVICE $SERVICE_NAME..."
 deleteKongItem "services" $SERVICE_NAME
 CMD=$(echo "curl -s -X POST \
   $URL_KONG/services/ \
   -H 'Content-Type: application/json' \
   -d '{
   \"url\": \"$SERVICE_URL\",
   \"name\": \"$SERVICE_NAME\",
   \"retries\": 5,
   \"read_timeout\": 60000,
   \"write_timeout\": 60000}'")
 if [ "$DEBUG" -eq "1" ]; then
   echo ">CreateService: $CMD"
 fi
 SERVICE_ID=$(eval $CMD | python3 -c "import sys, json; print(json.load(sys.stdin)['id'])")
 echo " Added service $SERVICE_NAME=$SERVICE_ID"

}

addRoute2Service() {
    SERVICE_NAME=$1
    ROUTE_NAME=$2
    ROUTE_VERBS=$3
    ROUTE_PATHS=$4
    ROUTE_PRIORITY=$5
    ROUTE_STRIPPATH=$6
    ROUTE_PRESERVEHOST=$7
    if test -n "$8";
    then
	 ROUTE_PROTOCOLS=$8
    else
         ROUTE_PROTOCOLS=[\"http\",\"https\"]
    fi

    echo "  Adding route to $SERVICE_NAME.$ROUTE_NAME..."
    echo "             with ROUTE_VERBS=$ROUTE_VERBS"
    echo "             with ROUTE_PATHS=$ROUTE_PATHS"    
    echo "             with ROUTE_PROTOCOLS=$ROUTE_PROTOCOLS"
    CMD=$(echo "curl -s -X POST \
     $URL_KONG/services/$SERVICE_NAME/routes \
     -H 'Content-Type: application/json' \
     -d '{
           \"protocols\": $ROUTE_PROTOCOLS,
           \"methods\": $ROUTE_VERBS,
           \"paths\": $ROUTE_PATHS,
           \"regex_priority\": $ROUTE_PRIORITY,
           \"strip_path\": $ROUTE_STRIPPATH,
           \"preserve_host\": $ROUTE_PRESERVEHOST
    }'")    
    if [ "$DEBUG" -eq "1" ]; then
      echo "$GAP>$CMD"
    fi
    ROUTE_ID=$(eval $CMD | python3 -c "import sys, json; print(json.load(sys.stdin)['id'])")
    echo " Added route to $SERVICE_NAME.$ROUTE_NAME=$ROUTE_ID"
}


create_urlRedirect() {
    #Example: create_urlRedirect PRO17_0328_socialMoriarty 'http://argon-solr:8975/solr/PRO17_0328_socialMoriarty/select' '/web-server/rest/documents/select' 0
    ITEM_NAME=$1
    ROUTE_NAME=R_$1
    URL1=$2
    URL2=$3
    ADDSECURITY=$4

    echo "**** Configuring $ITEM_NAME... ****"
    deleteKongItem "services" $ITEM_NAME
    echo "Adding service $ITEM_NAME"
    CMD=$(echo "curl -s -X POST \
      $URL_KONG/services/ \
      -H 'Content-Type: application/json' \
      -d '{
        \"url\": \"$URL1\",
        \"name\": \"$ITEM_NAME\",
        \"retries\": 5,
        \"read_timeout\": 60000,
        \"write_timeout\": 60000
    }'")
   
    SERVICE_ID=$(eval $CMD | python3 -c "import sys, json; print(json.load(sys.stdin)['id'])")

    echo Adding route to $ROUTE_NAME...
    ROUTE_NAME=$ROUTE_NAME
    CMD=$(echo "curl -s -X POST \
     $URL_KONG/services/$ITEM_NAME/routes \
     -H 'Content-Type: application/json' \
     -d '{
           \"protocols\": [\"http\",\"https\"],
           \"methods\": $ALL_VERBS,
           \"paths\": [\"$URL2\"],
           \"regex_priority\": 1,
           \"strip_path\": true,
		   \"preserve_host\": true
    }'")
    # echo $CMD
    ROUTE_ID=$(eval $CMD | python3 -c "import sys, json; print(json.load(sys.stdin)['id'])")
    if [ "$ADDSECURITY" = "false" ] ; then
      echo "No Security added to route $ROUTE_NAME"
    else
      echo "Adding Security to route $ROUTE_NAME"
      addSecurityToRoute $ROUTE_ID
    fi
}


enable_cors() {  
  echo "PENDING TO BE FINISHED!"
  SERVICE_NAME=$1
  SERVICE_URL_BASE=$2
  echo "**** Enabling CORS ON service $SERVICE_NAME... ****"
  CMD=$(echo "curl -s -X POST \
      $URL_KONG/services/$SERVICE_NAME/plugins \
    --data \"name=cors\"  \
    --data \"config.origins=$SERVICE_URL_BASE\" \
    --data \"config.methods=GET\" \
    --data \"config.methods=POST\" \
    --data \"config.headers=Accept\" \
    --data \"config.headers=Accept-Version\" \
    --data \"config.headers=Content-Length\" \
    --data \"config.headers=Content-MD5\" \
    --data \"config.headers=Content-Type\" \
    --data \"config.headers=Date\" \
    --data \"config.headers=X-Auth-Token\" \
    --data \"config.exposed_headers=X-Auth-Token\" \
    --data \"config.credentials=true\" \
    --data \"config.max_age=3600\"")
}

check(){
  if [ $1 -ne 0  ] ;then echo ${txtbld}$(tput setaf 1)  error in execution $(tput sgr0)  ; exit 1; fi
}
########################################
### SECTION UTILITY METHODS  (END  ) ###
########################################


##########################################
### CONFIGURATION METHODS (BEGIN) ########
##########################################
configureArgonWA() {
    echo "......   ARGONWA ............."
    createService argonwa "http://argon-webapp:8000"
    addRoute2Service argonwa route-argonwa "$ALL_VERBS" "[\"/argonwa\"]" 6 false true
    addSecurityToRoute $ROUTE_ID
}


configureContainerManager() {
    echo "......   CONTAINER MANAGER ............."
    createService containerManager "http://argon-containermanager:9999"
    addRoute2Service containerManager route-cm  "$ALL_VERBS" "[\"/cm\"]" 6 false true

}


configureJetty() {
    echo "......   JETTY ............."
    createService jetty "http://argon-jetty:8080"
    addRoute2Service jetty route-meditorClassicUI  "$ALL_VERBS" "[\"/meditorclassicui\"]" 6 false true
    addSecurityToRoute $ROUTE_ID
    addRoute2Service jetty route-meditorClassicUI  "$ALL_VERBS" "[\"/edit\"]" 6 false true
    addSecurityToRoute $ROUTE_ID
}


configureM3() {
    echo "....M3 editor..........."
    SERVICE_NAME=m3editorclassic
    createService $SERVICE_NAME "http://argon-m3editorclassic:9999"
    addRoute2Service $SERVICE_NAME route-m3editorclassic  "$ALL_VERBS" "[\"/m3editorclassic/*\"]" 6 true true
    addSecurityToRoute $ROUTE_ID

    echo "......   M3 RestAPI ............."
    SERVICE_NAME=m3restapi
    createService $SERVICE_NAME "http://argon-m3restapi:9999"
    addRoute2Service $SERVICE_NAME route-m3restapi "$ALL_VERBS" "[\"/m3restapi\"]" 6 true true
    addSecurityToRoute $ROUTE_ID
    addRoute2Service $SERVICE_NAME route-m3restapiOldAPI "$ALL_VERBS" "[\"/web-server\"]" 6 true true
 

    echo "...M3EDITOR.. NODEJS..........."
    SERVICE_NAME=m3editor
    createService $SERVICE_NAME "http://argon-m3editor:3301"
    addRoute2Service $SERVICE_NAME route-m3editor "$ALL_VERBS" "[\"/meditor\"]" 6 false true
    addSecurityToRoute $ROUTE_ID
}


configureNodejs() {
    echo "....NODEJS..........."
    SERVICE_NAME=nodejs
    createService $SERVICE_NAME "http://argon-nodejs:3301"
    addRoute2Service $SERVICE_NAME route-nodejs "$ALL_VERBS" "[\"/node\"]" 6 false true
    addSecurityToRoute $ROUTE_ID
}

configureMongoViewer() {
    echo "....MONGO VIEWER..........."
    SERVICE_NAME=mongoViewer
    createService $SERVICE_NAME "http://argon-mongoviewer:8081"
    addRoute2Service $SERVICE_NAME route-mongoViewerDb "$ALL_VERBS" "[\"/db\"]" 6 false true
    addSecurityToRoute $ROUTE_ID
    addRoute2Service $SERVICE_NAME route-mongoViewer "$ALL_VERBS" "[\"/mviewer\"]" 6 true true
    addSecurityToRoute $ROUTE_ID
    addRoute2Service $SERVICE_NAME route-mongoViewerPublic "$ALL_VERBS" "[\"/public\"]" 6 false true

}

configurePublicWeb() {
    echo "....OPENDATA WEB..........."
    SERVICE_NAME=opendata
    createService $SERVICE_NAME "http://argon-jetty:8080"
    addRoute2Service $SERVICE_NAME route-opendata "$ALL_VERBS" "[\"/opendata\"]" 6 false true

}


configureJupyter() {
    echo "....JUPYTER..........."
    SERVICE_NAME=jupyter
    createService $SERVICE_NAME "http://argon-jupyterhub:8888"
    addRoute2Service $SERVICE_NAME route-jupyter "$ALL_VERBS" "[\"/jupyter\"]" 6 false true
    addSecurityToRoute $ROUTE_ID
   
}

configureSolr() {
    echo "....SOLR..........."
    SERVICE_NAME=solr
    createService $SERVICE_NAME "http://argon-solr:8975"
    addRoute2Service $SERVICE_NAME route-solr "$ALL_VERBS" "[\"/solr\"]" 6 false true
    addSecurityToRoute $ROUTE_ID
	
	
	
	
}

configureVirtuoso() {
    echo "....Virtuoso..........."
    SERVICE_NAME=virtuoso
    createService $SERVICE_NAME "http://argon-virtuoso:8890"
    addRoute2Service $SERVICE_NAME route-conductor "$ALL_VERBS" "[\"/conductor\"]" 6 false true
	addRoute2Service $SERVICE_NAME route-sparql "$ALL_VERBS" "[\"/sparql\"]" 6 false true
    
}

configureKong() {
    createUser admin adminPassword
    createUser user userPassword

    configureContainerManager
    configureJetty
    configureNodejs
    configureMongoViewer
    configureJupyter
    configureSolr
    configureVirtuoso
    configureArgonWA
    configureM3	
	configurePublicWeb
	configureRedirect
		
	
}

configureRedirect()
{
	create_urlRedirect opendataSolr 'http://argon-solr:8975/solr/opendata/select' '/web-server/rest/documents/select' 0	
}


##########################################
### CONFIGURATION METHODS (END) ##########
##########################################



printHelp
while getopts ":hsurca" opt; do
  case ${opt} in
    h )
      exit 0
      ;;
    s )
      ITEM_ID=$2
      echo $(curl -s -X GET $URL_KONG/services/$ITEM_ID)
      exit 0
      ;;
    u )
      ITEM_ID=$2
      echo $(curl -s -X GET $URL_KONG/consumers/$ITEM_ID)
      exit 0
      ;;

    r )
      ITEM_ID=$2
      echo $(curl -s -X GET $URL_KONG/services/$ITEM_ID/routes)
      exit 0
      ;;
    c )
      ITEM_ID=$2
      echo $(curl -s -X GET $URL_KONG/certificates/$ITEM_ID)
      exit 0
      ;;
    a ) # No interactive: 
      echo
      echo "load funtions and execute method after the && "
      ;;
    \? )
      echo
      echo "Invalid Option: -$OPTARG" 1>&2
      exit 1
      ;;
  esac
done

#echo Executing $0 $1 $2
if [ "$0" = "sh" ]; then
    echo execute form ansible...
else
    echo "Nothing to do"
    # createConfig 
fi
if [ "$DEBUG" -eq "1" ]; then
echo ">DEBUG MODE ON"
else
echo ">DEBUG MODE OFF"
fi
