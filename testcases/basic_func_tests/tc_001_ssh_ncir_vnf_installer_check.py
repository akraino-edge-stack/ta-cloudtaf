import sys
import os
import common_utils

from robot.libraries.BuiltIn import BuiltIn
from robot.api import logger

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '../libraries/common'))

ex = BuiltIn().get_library_instance('execute_command')


def tc_001_ssh_ncir_vnf_installer_check():
    steps = ['step1_check_ncir_vnf_installer_status']
    common_utils.keyword_runner(steps)


def step1_check_ncir_vnf_installer_status():
    check_ncir_vnf_installer_status()


def check_ncir_vnf_installer_status():
    command = 'systemctl status ncir_vnf_installer.service | grep -c "NCIR CAAS deploy END success"'
    stdout = ex.execute_unix_command(command)
    if stdout == "1":
        logger.console("NCIR CAAS deploy END success")
    else:
        log_command = "journalctl -u ncir_vnf_installer"
        filename = "tc001.log"
        log_dir = os.path.join(os.path.dirname(__file__))
        common_utils.gather_logs(log_command, filename, log_dir)
        raise Exception("NCIR CAAS deploy failed !")
