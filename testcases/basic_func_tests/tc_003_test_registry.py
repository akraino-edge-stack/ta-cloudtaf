import sys
import os
from robot.libraries.BuiltIn import BuiltIn
from robot.api import logger
from test_constants import *

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '../libraries/common'))
import common_utils  # noqa


ex = BuiltIn().get_library_instance('execute_command')
stack_infos = BuiltIn().get_library_instance('stack_infos')
crf_nodes = stack_infos.get_crf_nodes()
all_nodes = stack_infos.get_all_nodes()
temp_image_tag = 'test'


def tc_003_test_registry():
    steps = ['step_1_test_registry']
    common_utils.keyword_runner(steps)


def step_1_test_registry():
    docker_img_tag_command = "docker images | grep {0} | awk '{{ print $2 }}' | head -n1".format(test_image)
    image_tag = ex.execute_unix_command(docker_img_tag_command).strip()
    image = reg + ':' + reg_port + '/' + reg_path + '/' + test_image + ':' + image_tag
    command = 'docker rmi ' + image + '; docker pull ' + image + '; docker push ' + image
    logger.console("")
    for key in all_nodes:
        ex.execute_unix_command_on_remote_as_root(command, all_nodes[key], delay="30s",)
        logger.console(key + ": registry reachable.")
