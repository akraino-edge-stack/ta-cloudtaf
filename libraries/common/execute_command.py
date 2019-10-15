import re
import time
from robot.libraries.BuiltIn import BuiltIn
from robot.libraries.String import String
from robot.api import logger
from datetime import datetime
from datetime import timedelta
from decorators_for_robot_functionalities import *
from users import *
from test_constants import *


class execute_command:
    def __init__(self):
        self._builtin = BuiltIn()
        self._string = String()
        self._builtin.import_library('SSHLibrary')
        self._sshlibrary = self._builtin.get_library_instance('SSHLibrary')
        self._default_user = {}
        self._prompt = ':prompt:'
        self._local_infra_int_ip_ipv4 = ''
        self._key_exists = False

    def get_ssh_library_instance(self):
        return self._sshlibrary

    def get_default_user(self):
        return self._default_user

    @Robot_log
    def check_if_login_was_successful(self, login_output):
        login_errors = ['authentication failure', 'name or service not known', 'permission denied']
        for login_error in login_errors:
            if re.search(login_error, login_output, re.IGNORECASE):
                return False
        return True

    @Robot_log
    def open_connection_and_log_in(self, host, user, private_key=None, timeout="90s"):
        self._sshlibrary.open_connection(host=host, timeout=timeout)
        login_output = ''
        wait_until = datetime.now() + timedelta(seconds=60)
        while (datetime.now() < wait_until):
            time.sleep(1)
            try:
                if private_key is None:
                    login_output = self._sshlibrary.login(user['username'], user['password'])
                else:
                    login_output = self._sshlibrary.login_with_public_key(user['username'], private_key, user['password'])
            except Exception as err:
                logger.warn("Login was unsuccessful, trying again.")
                continue
            if self.check_if_login_was_successful(login_output):
                self._configure_prompt()
                logger.info("Login was successful.")
                break
        return login_output

    @Robot_log
    def set_basic_connection(self, user, private_key=None):
        self._default_user = user
        stack_infos = self._builtin.get_library_instance('stack_infos')
        self.open_connection_and_log_in(stack_infos.get_floating_ip(), user, private_key)
        self._local_infra_int_ip_ipv4 = self.get_interface_ipv4_address(stack_infos.get_crf_nodes())
        self._key_exists = self.check_id_rsa_exists()
        self.stop_auditd_service()

    @Robot_log
    def _configure_prompt(self):
        self._sshlibrary.write('export PS1=' + self._prompt)
        self._sshlibrary.read_until_regexp('(?m)^' + self._prompt + '.*')

    @Robot_log
    def su_as(self, user):
        def check_if_su_was_succesful(login_output):
            if 'incorrect password' in login_output or 'Authentication failure' in login_output:
                return False
            return True

        self._sshlibrary.write('su ' + user['username'])
        self._sshlibrary.read_until('Password:')
        self._sshlibrary.write(user['password'])
        output = self._sshlibrary.read_until(self._prompt)
        if not check_if_su_was_succesful(output):
            raise Exception(output)

    @Robot_log
    def sudo_as_root(self):
        self._sshlibrary.write('sudo -s')
        self._sshlibrary.read_until(self._prompt)

    @Robot_log
    def exit_from_user(self):
        self._sshlibrary.write('exit')
        self._sshlibrary.read_until(self._prompt)


    @Robot_log
    def execute_unix_command(self,
                             command,
                             fail_on_non_zero_rc=True,
                             delay="90s",
                             skip_prompt_in_command_output=False,
                             user={}):
        """
        This method executes a linux command via the SSHlibrary connection.
        The user account which issues the command, is the same as which the connection has opened for (by default)
        The command can be also executed by switching (su) to another user (e.g. parameter usage: user = "root")

        :param command:
        :param fail_on_non_zero_rc: the command will fail if return code is nonzero
        :param delay:
        :param skip_prompt_in_command_output:
        :param user: switch to user, by default the command is executed with the current user
        for which the ssh connection was opened

        :return: stdout: command output is returned
        """
        user_changed = False
        self._sshlibrary.set_client_configuration(timeout=delay)
        if user == root:
            self.sudo_as_root()
            user_changed = True
        elif bool(user) and user != self._default_user:
            self.su_as(user)
            user_changed = True

        self._sshlibrary.write(command)
        try:
            if skip_prompt_in_command_output:
                stdout = self._sshlibrary.read_until_regexp("(^|\n| )" + self._prompt + "$")
            else:
                stdout = self._sshlibrary.read_until(prompt)
        except Exception as err:
            stdout = unicode(err)
            ctrl_c = self._builtin.evaluate('chr(int(3))')
            self._sshlibrary.write_bare(ctrl_c)
            self._sshlibrary.read_until(prompt)
        stdout = re.sub(prompt + '$', '', stdout).strip()
        self._sshlibrary.write('echo error code: $?')
        error_code = self._sshlibrary.read_until(prompt)
        logger.trace("Error code variable value (befor processing)=" + error_code)
        error_code = self._string.get_lines_matching_regexp(error_code, pattern='error code: \\d+').split(':')[1].strip()
        logger.trace("Error code variable value (after processing)=" + error_code)
        self._sshlibrary.set_client_configuration(timeout="60s")
        if user_changed:
            self.exit_from_user()
        fail_on_non_zero_rc = self._builtin.convert_to_boolean(fail_on_non_zero_rc)
        if fail_on_non_zero_rc:
            if '0' != error_code:
                raise Exception('command: ' + command + '\nreturn code: ' + error_code + '\noutput: ' + stdout)
            return stdout
        else:
            return [stdout, error_code]

    @Robot_log
    def execute_unix_command_as_root(self,
                                     command,
                                     fail_on_non_zero_rc=True,
                                     delay="90s",
                                     skip_prompt_in_command_output=False):
        return self.execute_unix_command(command, fail_on_non_zero_rc, delay, skip_prompt_in_command_output, root)

    @Robot_log
    def ssh_to_another_node(self, host, user):
        self._sshlibrary.write('ssh ' + user['username'] + '@' + host + ' -o "StrictHostKeyChecking no"')
        if not self._key_exists:
            logger.info("Login with password")
            self._sshlibrary.read_until("'s password:")
            self._sshlibrary.write(user['password'])
        ssh_regexp = re.compile(r"\[{0}@.*$|authentication failure|name or service not known|permission denied".format(user["username"]), re.IGNORECASE)
        stdout = self._sshlibrary.read_until_regexp(ssh_regexp)
        if not self.check_if_login_was_successful(stdout):
            raise Exception("Login to another node FAILED")
        self._configure_prompt()

    @Robot_log
    def execute_unix_command_on_remote_as_root(self,
                                               command,
                                               host,
                                               user={},
                                               fail_on_non_zero_rc=True,
                                               delay="90s",
                                               skip_prompt_in_command_output=False):
        if self._local_infra_int_ip_ipv4 != host:
            if not user:
                user = self._default_user
            self.ssh_to_another_node(host, user)
            output = self.execute_unix_command_as_root(command, fail_on_non_zero_rc, delay, skip_prompt_in_command_output)
            self._sshlibrary.write('exit')
            self._sshlibrary.read_until(self._prompt)
        else:
            output = self.execute_unix_command_as_root(command, fail_on_non_zero_rc, delay, skip_prompt_in_command_output)
        return output

    @Robot_log
    def execute_unix_command_on_remote_as_user(self,
                                               command,
                                               host,
                                               user={},
                                               fail_on_non_zero_rc=True,
                                               delay="90s",
                                               skip_prompt_in_command_output=False):
        if not user:
            user = self._default_user
        if self._local_infra_int_ip_ipv4 != host:
            self.ssh_to_another_node(host, user)
            output = self.execute_unix_command(command, fail_on_non_zero_rc, delay, skip_prompt_in_command_output, user=user)
            self._sshlibrary.write('exit')
            self._sshlibrary.read_until(self._prompt)
        else:
            output = self.execute_unix_command(command, fail_on_non_zero_rc, delay, skip_prompt_in_command_output, user=user)
        return output

    @Robot_log
    def get_interface_ipv4_address(self, nodes):
        for key in nodes:
            if self.execute_unix_command("ip a | grep " + nodes[key] + " | wc -l") == "1":
                return nodes[key]

    @Robot_log
    def get_interface_ipv6_address(self, interface):
        return self.execute_unix_command_as_root('ip addr list ' + interface + ' | grep --color=no -o -P "(?<=inet6 ).*(?=/.*)"')

    @Robot_log
    def check_id_rsa_exists(self):
        stdout, err_code = self.execute_unix_command("ls /home/{0}/.ssh/id_rsa".format(self._default_user["username"]), fail_on_non_zero_rc=False)
        return err_code == '0'

    @Robot_log
    def stop_auditd_service(self):
        stack_infos = self._builtin.get_library_instance('stack_infos')
        if stack_infos.get_virtual_env():
            all_nodes = stack_infos.get_all_nodes()
            if not all_nodes:
                logger.info("Nodes dictionary is empty, nothing to check.")
                return
            for node in all_nodes.itervalues():
                command = "sed -i \"s#RefuseManualStop=yes#RefuseManualStop=no#g\" /usr/lib/systemd/system/auditd.service"
                self.execute_unix_command_on_remote_as_root(command, node)
                command = "systemctl daemon-reload"
                self.execute_unix_command_on_remote_as_root(command, node)
                command = "systemctl stop auditd.service"
                self.execute_unix_command_on_remote_as_root(command, node)


