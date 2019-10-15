#!/usr/bin/python

import os
import requests
import paramiko
import sys
from users import *

WORK_DIR = os.getenv('WORKDIR')
REG = os.getenv('REG')
REG_PORT = os.getenv('REG_PORT')
REG_PATH = os.getenv('REG_PATH')

sys.path.append(os.path.join(WORK_DIR, 'libraries', 'common'))

IP = os.getenv('SUT_IP')
CONTAINERS_DIR = os.path.join(WORK_DIR, 'resources', 'test_containers')
CHARTS_DIR = os.path.join(WORK_DIR, 'resources', 'test_charts')


def open_connection(host, user, pw):
    print("Open paramiko connection to {} with user: {} pass: {}".format(host, user, pw))
    client = paramiko.SSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy)
    client.connect(host, username=user, password=pw)
    return client


def create_remote_dir(client, remote_dir):
    execute_command(client, "rm -rf {}".format(remote_dir))
    execute_command(client, "mkdir -p {}".format(remote_dir))


def delete_remote_dir(client, remote_dir):
    execute_command(client, "rm -rf {}".format(remote_dir))


def execute_command(client, command):
    stdin, stdout, stderr = client.exec_command(command)
    print("The following command executed on remote: {}".format(command))
    stdout = stdout.read()
    print('stdout:', stdout)
    err = stderr.read()
    if err:
        raise Exception("The following error occured: {}".format(err))
    else:
        return stdout


def get_all_files_in_local_dir(local_dir, extension=""):
    all_files = list()
    if os.path.exists(local_dir):
        files = os.listdir(local_dir)
        for file in files:
            filename, ext = os.path.splitext(file)
            if extension in ext:
                filepath = os.path.join(local_dir, file)
                print "filename:" + filepath
                if os.path.isdir(filepath):
                    all_files.extend(get_all_files_in_local_dir(filepath))
                else:
                    all_files.append(filepath)
    else:
        print '{} folder does not exist'.format(local_dir)
    return all_files


def upload_resources(client, local, remote):
    sftp = client.open_sftp()
    for file in local:
        remote_path = os.path.join("{}{}".format(remote, file.split(remote.split('/')[-1])[1]))
        remote_dir = remote_path.rsplit('/', 1)[0]
        execute_command(client, "mkdir -p {}".format(remote_dir))
        sftp.put(file, remote_path)
    print("Upload {} from robot container to the SUT {}".format(local, remote))


def load_docker_images_from_directory(client, remote_dir):
    command = "ls {}".format(remote_dir)
    docker_images = execute_command(client, command).splitlines()
    for image in docker_images:
        command = "docker load -i {}/{}".format(remote_dir, image)
        execute_command(client, command)
        image_name = image.rsplit('.tar')[0]
        print image_name
        command = "docker push {}:{}/{}/{}".format(REG, REG_PORT, REG_PATH, image_name)
        execute_command(client, command)


def create_helm_packages(client, remote_dir):
    command = "helm repo list"
    stdout = execute_command(client, command)
    chart_repo = stdout.splitlines()[1].split()[1]
    command = "ls {}".format(remote_dir)
    helm_charts = execute_command(client, command).splitlines()
    for chart in helm_charts:
        command = "helm package {}/{}".format(remote_dir, chart)
        helm_package_path = execute_command(client, command)
        helm_package = helm_package_path.split(cloudadmin['username'] + '/')[1].rstrip()
        print helm_package
        command = "curl -sS -XPOST -H 'Content-Type: application/gzip' --data-binary @{} {}/charts/{}".format(
            helm_package, chart_repo, helm_package)
        execute_command(client, command)
        command = "rm -f {}".format(helm_package_path)
        execute_command(client, command)
    command = "helm repo update"
    execute_command(client, command)


def main():

    paramiko_client = open_connection(IP, cloudadmin['username'], cloudadmin['password'])
    remote_containers_dir = os.path.join("/home/{}/resources/test_containers".format(cloudadmin['username']))
    container_images = get_all_files_in_local_dir(CONTAINERS_DIR, "tar")
    remote_test_charts_dir = os.path.join("/home/{}/resources/test_charts".format(cloudadmin['username']))
    test_charts = get_all_files_in_local_dir(CHARTS_DIR)

    try:
        create_remote_dir(paramiko_client, remote_containers_dir)
        create_remote_dir(paramiko_client, remote_test_charts_dir)
        upload_resources(paramiko_client, container_images, remote_containers_dir)
        upload_resources(paramiko_client, test_charts, remote_test_charts_dir)
        load_docker_images_from_directory(paramiko_client, remote_containers_dir)
        create_helm_packages(paramiko_client, remote_test_charts_dir)
        delete_remote_dir(paramiko_client, remote_test_charts_dir)
        delete_remote_dir(paramiko_client, remote_containers_dir)

    finally:
        paramiko_client.close()


if __name__ == "__main__":
    main()
