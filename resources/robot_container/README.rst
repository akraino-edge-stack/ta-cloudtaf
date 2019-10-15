Introduction
------------

Containerized test environment to run functional tests on CAAS deployments. Test cases are written in python, 
executed with Robot Framework using Pabot parallel executor for robot.

The container will contain the test resources including the helm charts and container images for the test applications,
test cases and the scripts needed for the execution.


Environment setup
-----------------

Few config parameters should be set in resources/scripts/include/robot_container.env

| ROBOT_CONTAINER_TAG: tag of the executor container
| TC_TAG: test cases will be executed indicated with this tag
| SUT_IP: controller-1 node IP of the deployment
| SKIP_BM_ONBOARD if false test applications onboard will be skipped (this is useful for re-execution)
| PASSWORD: password for cloudadmin user

These parameters should be set for manual execution, otherwise these are set by the jenkins test job
(currently http://jenkins2.mtlab.att-akraino.org/job/Test_cloudtaf_modifications/)


Building the environment
------------------------

resources/scripts/build-test-containers.sh script builds the test containers located in resources/test_containers/ folder.

resources/scripts/robot-test-build.sh script builds the robot executor container


Executing tests
---------------

resources/scripts/robot-test-run.sh script starts the robot container. The entrypoint is the robot-deployment-test.sh
script, this will perform the onboarding of the test application, and execute the test suites parallelly from folder
testcases/parallel_suites/.
The robot logs will be available in pabot_logs folder.

Test cases can be executed separately with command like
python -m robot -t "CAAS_BASIC_FUNC_002" --variable floating_ip:<SUT_IP>  --loglevel trace ssh_check.robot
In this case please check the installed packages in the Dockerfile.

Another option is to start the executor container based on the resources/scripts/robot-test-run.sh script overriding the
entrypoint with option --entrypoint=/bin/bash