#!/usr/bin/python

import os
import requests
import paramiko
import sys

WORK_DIR = os.getenv('WORKSPACE')
TEST_DIR = os.path.join(WORK_DIR, 'test')

sys.path.append(os.path.join(TEST_DIR, 'common'))
from users import *

IP = os.getenv('SUT_IP')
ARTY_LOGIN = os.getenv('ARTY_LOGIN')
ARTY_PASS_HASH = os.getenv('ARTY_PASS_HASH')
ARTY_REPO_URL = os.getenv('ARTY_REPO_URL')
ARTY_APP_IMAGE_DIR = os.getenv('ARTY_APP_IMAGE_DIR')
VERSION_SH = os.path.join(WORK_DIR, 'build-config-files', 'version.sh')
APP_IMAGE_DIR = os.path.join(TEST_DIR, 'app-image')


def get_latest_app_image_version(version_path):
    with open(version_path, 'r') as versions:
        for version in versions:
            if "APP_IMAGE_VERSION" in version:
                name, value = version.replace('export', '').strip().replace('"', '').split('=')
                return value


def create_local_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)
    print("Create local dir for the app image: {}".format(path))


def download_file_from_arty(arty_url, user, pw, download_path):
    r = requests.get(arty_url, auth=(user, pw))
    if not r.ok:
        raise Exception("{} download failed!".format(arty_url))
    open(download_path, 'wb').write(r.content)
    print("Download {} and save to {}".format(arty_url, download_path))


def open_connection(host, user, pw):
    print("Open paramiko connection to {} with user: {} pass: {}".format(host, user, pw))
    client = paramiko.SSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy)
    client.connect(host, username=user, password=pw)
    return client

def upload_file(client, local, remote):
        sftp = client.open_sftp()
        sftp.put(local, remote)
        print("Upload {} from jenkins container to the SUT {}".format(local, remote))


def execute_command(client, command):
    stdin, stdout, stderr = client.exec_command(command)
    print("The following command executed on remote: {}".format(command))
    print('stdout:', stdout.read())
    err = stderr.read()
    if err:
        raise Exception("The following error occured: {}".format(err))


def main(arty__app_img_url=None):
    app_image_version = get_latest_app_image_version(VERSION_SH)
    latest_app_img = "test_app-" + app_image_version

    if not arty__app_img_url:
        arty__app_img_url = "{}/{}/{}".format(ARTY_REPO_URL, ARTY_APP_IMAGE_DIR, latest_app_img)
    ansible_command = '/usr/bin/ansible-playbook -i /opt/nokia/caas_lcm/deploy/inventory ' \
                      '/opt/nokia/caas_lcm/deploy/playbook_bm_onboard.yml ' \
                      '-e "app_image_name={}"'.format(latest_app_img)

    create_local_dir(APP_IMAGE_DIR)
    app_image_local = os.path.join(APP_IMAGE_DIR, latest_app_img)
    app_image_remote = os.path.join("/home/{}/{}".format(cloudadmin['username'], latest_app_img))

    download_file_from_arty(arty__app_img_url, ARTY_LOGIN, ARTY_PASS_HASH, app_image_local)

    paramiko_client = open_connection(IP, cloudadmin['username'], cloudadmin['password'])
    try:
        upload_file(paramiko_client, app_image_local, app_image_remote)
        execute_command(paramiko_client, ansible_command)
    finally:
        paramiko_client.close()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description='This script onboards an app-image on the host '
                    'wich represented by the SUT_IP env var.',
        usage='If the script is called without any parameters the latest app-image will be used.')
    parser.add_argument('--app_image_url', help='Full artifactory image url path.', dest='app_url')
    args = parser.parse_args()
    main(args.app_url)
