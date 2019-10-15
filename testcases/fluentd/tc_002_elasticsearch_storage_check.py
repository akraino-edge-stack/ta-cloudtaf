import sys
import os
import datetime
import json
import common_utils
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '../common'))
from decorators_for_robot_functionalities import *
from robot.libraries.BuiltIn import BuiltIn
from robot.api import logger
from test_constants import *
from users import *

ex = BuiltIn().get_library_instance('execute_command')


def tc_002_elasticsearch_storage_check():
    steps = ['step1_get_elasticsearch_kubernetes_data', 'step2_check_plugins']
    if check_if_test_should_be_run:
        common_utils.keyword_runner(steps)


def check_if_test_should_be_run():
    command = "cmcli get-property --property cloud.caas " \
              "grep '\"infra_log_store\": \"elasticsearch\"' | wc -l"
    if ex.execute_unix_command(command) != '1':
        command = "cat {} | grep 'infra_log_store: elasticsearch' | wc -l".format(USER_CONFIG_PATH)
        return ex.execute_unix_command(command) == '1'
    return True


@Robot_log
def elasticsearch_get_field(field):
    data = '{ "size": 1, ' \
           '"query": { ' \
                '"exists": { "field": "' + field + '" } }, ' \
                '"sort" : [ {"@timestamp" : {"order" : "desc"}} ] }'
    header = "Content-Type: application/json"
    es_index = "_all"
    url = "{}/{}/_search".format(ELASTICSEARCH_URL, es_index)
    request = "--header '{}' --request POST --data '{}' {}".format(header, data, url)

    resp = ex.execute_unix_command("curl {}".format(request))
    return json.loads(resp)


@Robot_log
def elasticsearch_parse_field(msg, field):
    if 'hits' not in msg:
        msg = elasticsearch_get_field(field)
        if 'hits' not in msg:
            raise Exception('hits key not found in the following input:\n {}'.format(json.dumps(msg)))
    msglen = len(msg['hits']['hits'])
    output = {}
    for i in range(msglen):
        output['date'] = (msg['hits']['hits'][i]['_source']['@timestamp'])
        output['tag'] = (msg['hits']['hits'][i]['_source'][field])
    logger.info(output)
    return output


def step1_get_elasticsearch_kubernetes_data():
    field = "kubernetes"
    resp = elasticsearch_get_field(field)
    output = elasticsearch_parse_field(resp, field)
    if len(output) == 0:
        raise Exception("Logs with field {} not found!".format(field))


def is_there_some_plugin(elastic_plugins):
    return elastic_plugins.find("reindex") != -1


def step2_check_plugins():
    command = "curl http://elasticsearch-logging.kube-system.svc.nokia.net:9200/_cat/plugins?v"
    elastic_plugins = ex.execute_unix_command_as_root(command)
    if is_there_some_plugin(elastic_plugins):
        logger.info("Installed elastic search plugins:" + elastic_plugins)
    else:
        raise Exception("No plugin named 'reindex' is installed inside elasticsearch, something not right!")
