#!/bin/bash -ex

env_file=${1:-include/robot_container.env}
source ${env_file}
test_conatiners=`ls ../test_containers/`
for val in $test_conatiners 
do
    echo "### Building $val test container"
    
    docker build --network=host --no-cache --build-arg HTTP_PROXY="${http_proxy}" --build-arg HTTPS_PROXY="${https_proxy}" --build-arg NO_PROXY="${no_proxy}" --build-arg http_proxy="${http_proxy}" --build-arg https_proxy="${https_proxy}" --build-arg no_proxy="${no_proxy}" --tag ${REG}:${REG_PORT}/${REG_PATH}/${val}:latest ../test_containers/${val}/
    
    docker save ${REG}:${REG_PORT}/${REG_PATH}/${val}:latest -o ../test_containers/${val}.tar
    
    echo ${val} test container is saved to ../test_containers/${val}/${val}.tar
done








  
echo ">> Done"
