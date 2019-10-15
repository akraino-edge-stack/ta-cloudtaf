import os

prompt = ':prompt:'

int_if_name_in_openstack = 'infra-int'

reg = os.getenv('REG')
reg_port = os.getenv('REG_PORT')
reg_path = os.getenv('REG_PATH')
test_image = "kubernetespause"

source_folder = os.getenv('SOURCE_FOLDER')
vnf_id = os.getenv('STACK_ID')
cbam_py = "{}/scripts/cbam.py".format(source_folder)

registry_cert = '/etc/docker-registry/registry?.pem'
registry_key = '/etc/docker-registry/registry?-key.pem'
registry_cacert = '/etc/docker-registry/ca.pem'

ROBOT_LOG_PATH = "/tmp/"

registry = {'url': reg, 'port': reg_port}

int_sshd_config_name = "sshd_config_int"
ext_sshd_config_name = "sshd_config_ext"
sshd_port = "22"

dns_masq_port = "53"
kube_dns_port = "10053"
min_dns_replica = 1
max_dns_replica = 3
test_address1 = 'google.com'
test_address2 = 'tiller.kube-system.svc.nokia.net'

crf_node_openstack_file_types = ["user_config.yaml"]

pressure_default_timeout = 600

# TC014 constant
INFLUXDB_URL = "http://influxdb.kube-system.svc.nokia.net:8086"
GRAFANA_URL = "http://monitoring-grafana.kube-system.svc.nokia.net:8080"

# TC016 constant
docker_size_quota = '2G'

# TC Fluentd
ELASTICSEARCH_URL = "http://elasticsearch-logging.kube-system.svc.nokia.net:9200"
USER_CONFIG_PATH = "/opt/nokia/userconfig/user_config.yaml"
ES_IDX_PREFIX = "caas"

test_chart = dict(name="busybox3", release_name="custom-oper-test", chart_version="3.3.3",
                  repo="default/",
                  kube_objects=[dict(obj_type="pod", obj_name="busybox3", obj_count="1",
                                     namespace="kube-system")])

su_test_chart = dict(name="su-test", release_name="su-test", chart_version="1.1.1",
                     su_version="1.1.1", repo="default/",
                     kube_objects=[dict(obj_type="pod", obj_name="su-test", obj_count="10",
                                        namespace="kube-system")])

su_test_chart1 = dict(name="su-test", release_name="su-test", chart_version="1.1.2",
                      su_version="1.1.1", repo="default/",
                      kube_objects=[dict(obj_type="pod", obj_name="su-test", obj_count="10",
                                         namespace="kube-system")])

su_test_chart_f = dict(name="su-test_f", release_name="su-test", chart_version="1.1.4",
                       su_version="1.1.1", repo="default/",
                       kube_objects=[dict(obj_type="pod", obj_name="su-test_f", obj_count="10",
                                          namespace="kube-system")])

pv_test_pod = dict(obj_type="pod", obj_name="pv-test-deployment", obj_count="2", namespace="default")
pv_test_pvc = dict(obj_type="pvc", obj_name="pvc", obj_count="1", namespace="default")
kube_controller_manager = dict(obj_type="pod", obj_name="kube-controller-manager", obj_count="3", namespace="kube-system")
influxdb_service = dict(obj_type="service", obj_name="influxdb", obj_count="1", namespace="kube-system")
influxdb_deployment = dict(obj_type="deployment", obj_name="influxdb", obj_count="1", namespace="kube-system")
grafana_service = dict(obj_type="service", obj_name="monitoring-grafana", obj_count="1", namespace="kube-system")
grafana_deployment = dict(obj_type="deployment", obj_name="monitoring-grafana", obj_count="1", namespace="kube-system")
danmnet_pods1 = dict(obj_type="pod", obj_name="danmnet-pods1", obj_count="4", namespace="default",    ip_list=[])
danmnet_pods2 = dict(obj_type="pod", obj_name="danmnet-pods2", obj_count="3", namespace="default",    ip_list=[])
danmnet_pods3 = dict(obj_type="pod", obj_name="danmnet-pods3", obj_count="4", namespace="default",    ip_list=[])
danmnet_pods4 = dict(obj_type="pod", obj_name="danmnet-pods4", obj_count="5", namespace="kube-system",ip_list=[])
danmnet_pods5 = dict(obj_type="pod", obj_name="danmnet-pods5", obj_count="1", namespace="kube-system",ip_list=[])
danmnet_pods6 = dict(obj_type="pod", obj_name="danmnet-pods6", obj_count="6", namespace="default",    ip_list=[])
danmnet_pods7 = dict(obj_type="pod", obj_name="danmnet-pods7", obj_count="5", namespace="default",    ip_list=[])
danmnet_pods8 = dict(obj_type="pod", obj_name="danmnet-pods8", obj_count="1", namespace="default",    ip_list=[])
danmnet_pods9 = dict(obj_type="pod", obj_name="danmnet-pods9", obj_count="1", namespace="kube-system",ip_list=[])
danmnet_pods10 = dict(obj_type="pod", obj_name="danmnet-pods10", obj_count="1", namespace="default",  ip_list=[])
danmnet_pods11 = dict(obj_type="pod", obj_name="danmnet-pods11", obj_count="1", namespace="default",  ip_list=[])
danmnet_pods12 = dict(obj_type="pod", obj_name="danmnet-pods12", obj_count="1", namespace="default",  ip_list=[])
danmnet_pods13 = dict(obj_type="pod", obj_name="danmnet-pods13", obj_count="1", namespace="default",  ip_list=[])
danmnet_pods14 = dict(obj_type="pod", obj_name="danmnet-pods14", obj_count="1", namespace="default",  ip_list=[])
danmnet_pods_all = dict(obj_type="pod", obj_name="danmnet-pods", obj_count="0", namespace="default",    ip_list=[])

php_apache_pod = dict(obj_type="pod", obj_name="php-apache", obj_count="1", namespace="default")
podinfo_pod = dict(obj_type="pod", obj_name="podinfo", obj_count="2", namespace="kube-system")
load_generator_for_apache = dict(obj_type="pod", obj_name="load-generator-for-apache", obj_count="1", namespace="default")
http_traffic_gen = dict(obj_type="pod", obj_name="http-traffic-gen", obj_count="1", namespace="default")

pods_skipped = ['load-generator-for-apache', 'php-apache-deployment', 'pv-test-deployment', 'danmnet-pods',
                test_chart['kube_objects'][0]['obj_name'], 'registry-update', 'su-test', 'cpu-pooling', 'swift-update',
                'su-test', 'podinfo', 'tennet-pod']

services_skipped = ['selinux-policy-migrate-local-changes', 'cloud-final.service', 'kdump.service',
                    'postfix.service']

danmnets_properties = {
    'd_test-net1':   {'name':"test-net1", 'Validation':"true",  'NetworkType':"",        'namespace':"default",     'host_if':"", 'rt_tables':"201",  'routes':"", 'vxlan':"", 'vlan':""},
    'd_test-net2':   {'name':"test-net2", 'Validation':"true",  'NetworkType':"",        'namespace':"default",     'host_if':"vx_test-net2", 'rt_tables':"11", 'routes':"10.0.0.0/32: 10.0.0.50", 'vxlan':"50", 'vlan':""},
    'ks_test-net2':  {'name':"test-net2", 'Validation':"true",  'NetworkType':"",        'namespace':"kube-system", 'host_if':"vx_test-net2", 'rt_tables':"11", 'routes':"10.1.1.0/32: 10.1.1.1", 'vxlan':"50", 'vlan':""},
    'd_test-net4':   {'name':"test-net4", 'Validation':"true",  'NetworkType':"",        'namespace':"default",     'host_if':"", 'rt_tables':"13", 'routes':"", 'vxlan':"", 'vlan':""},
    'd_test-net5':   {'name':"test-net5", 'Validation':"true",  'NetworkType':"",        'namespace':"default",     'host_if':"", 'rt_tables':"14", 'routes':"", 'vxlan':"", 'vlan':""},
    'd_test-net6':   {'name':"test-net6", 'Validation':"true",  'NetworkType':"",        'namespace':"default",     'host_if':"vx_test-net6", 'rt_tables':"", 'routes':"", 'vxlan':"52", 'vlan':""},
    'd_test-net7':   {'name':"test-net7", 'Validation':"true",  'NetworkType':"",        'namespace':"default",     'host_if':"vx_test-net7", 'rt_tables':"15", 'routes':"", 'vxlan':"53", 'vlan':""},
    'd_test-net8':   {'name':"test-net8", 'Validation':"true",  'NetworkType':"",        'namespace':"default",     'host_if':"vx_test-net8", 'rt_tables':"15", 'routes':"10.10.0.0/32: 10.10.0.1", 'vxlan':"50", 'vlan':""},
    'd_test-net13':  {'name':"test-net13", 'Validation':"true",  'NetworkType':"",        'namespace':"default",    'host_if':"vx_test-net13", 'rt_tables':"20", 'routes':"", 'vxlan':"56", 'vlan':""},
    'd_test-net15':  {'name':"test-net15", 'Validation':"true",  'NetworkType':"",        'namespace':"default",    'host_if':"test-net15.1", 'rt_tables':"22", 'routes':"", 'vxlan':"", 'vlan':"1"},
    'd_test-net16':  {'name':"test-net16", 'Validation':"true",  'NetworkType':"",        'namespace':"default",    'host_if':"test-net16.4094", 'rt_tables':"23", 'routes':"", 'vxlan':"", 'vlan':"4094"},
    'd_test-net20':  {'name':"test-net20", 'Validation':"true",  'NetworkType':"",        'namespace':"default",    'host_if':"vx_test-net20", 'rt_tables':"27", 'routes':"", 'vxlan':"", 'vlan':""},
    'd_test-net21':  {'name':"test-net21", 'Validation':"true",  'NetworkType':"",        'namespace':"default",    'host_if':"vx_test-net21", 'rt_tables':"28", 'routes':"", 'vxlan':"16777214", 'vlan':""},
    'd_test-net23':  {'name':"test-net23", 'Validation':"true",  'NetworkType':"",        'namespace':"default",    'host_if':"vx_test-net23", 'rt_tables':"30", 'routes':"", 'vxlan':"", 'vlan':""},
    'd_test-net24':  {'name':"test-net24", 'Validation':"false", 'NetworkType':"flannel", 'namespace':"default",    'host_if':"", 'rt_tables':"31", 'routes':"", 'vxlan':"58", 'vlan':"57"},
    'd_test-net25':  {'name':"test-net25", 'Validation':"true",  'NetworkType':"",        'namespace':"default",    'host_if':"test-net25.58", 'rt_tables':"10", 'routes':"10.10.0.0/32: 10.10.0.40", 'vxlan':"", 'vlan':"58"},
    'd_test-net26':  {'name':"test-net26", 'Validation':"true",  'NetworkType':"",        'namespace':"default",    'host_if':"vx_test-net26", 'rt_tables':"10", 'routes':"", 'vxlan':"60", 'vlan':""},
    'ks_test-net27': {'name':"test-net27", 'Validation':"true",  'NetworkType':"",        'namespace':"kube-system",'host_if':"vx_test-net27", 'rt_tables':"10", 'routes':"", 'vxlan':"61", 'vlan':""},
    'd_test-net28':  {'name':"test-net28", 'Validation':"true",  'NetworkType':"",        'namespace':"default",    'host_if':"", 'rt_tables':"33", 'routes':"", 'vxlan':"50", 'vlan':""},
    'ks_test-net29': {'name':"test-net29", 'Validation':"true",  'NetworkType':"",        'namespace':"kube-system",'host_if':"", 'rt_tables':"34", 'routes':"", 'vxlan':"50", 'vlan':""},
    'd_test-net30':  {'name':"test-net30", 'Validation':"true",  'NetworkType':"",        'namespace':"default",     'host_if':"", 'rt_tables':"10", 'routes':"10.10.0.0/32: 10.10.0.40", 'vxlan':"", 'vlan':""},
}

danmnets_error = {
    'd_test-net3':   {'name':"test-net3", 'Validation':"false",  'NetworkType':"",       'namespace':"default",     'host_if':"", 'rt_tables':"12", 'routes':"", 'vxlan':"51", 'vlan':""},
    'd_test-net9':   {'name':"test-net9", 'Validation':"false",  'NetworkType':"",       'namespace':"default",     'host_if':"", 'rt_tables':"155", 'routes':"", 'vxlan':"55", 'vlan':""},
    'd_test-net10':  {'name':"test-net10", 'Validation':"false", 'NetworkType':"",        'namespace':"default",    'host_if':"", 'rt_tables':"18", 'routes':"", 'vxlan':"56", 'vlan':""},
    'd_test-net11':  {'name':"test-net11", 'Validation':"false", 'NetworkType':"",        'namespace':"default",    'host_if':"", 'rt_tables':"18", 'routes':"", 'vxlan':"55", 'vlan':""},
    'd_test-net12':  {'name':"test-net12", 'Validation':"false", 'NetworkType':"",        'namespace':"default",    'host_if':"", 'rt_tables':"19", 'routes':"", 'vxlan':"55", 'vlan':""},
    'd_test-net14':  {'name':"test-net14", 'Validation':"true", 'NetworkType':"",        'namespace':"default",    'host_if':"", 'rt_tables':"21", 'routes':"", 'vxlan':"", 'vlan':""},
    'd_test-net17':  {'name':"test-net17", 'Validation':"false", 'NetworkType':"",        'namespace':"default",    'host_if':"", 'rt_tables':"24", 'routes':"", 'vxlan':"", 'vlan':"4095"},
    'd_test-net18':  {'name':"test-net18", 'Validation':"false", 'NetworkType':"",        'namespace':"default",    'host_if':"", 'rt_tables':"25", 'routes':"", 'vxlan':"", 'vlan':"4096"},
    'd_test-net19':  {'name':"test-net19", 'Validation':"true", 'NetworkType':"",        'namespace':"default",    'host_if':"", 'rt_tables':"26", 'routes':"", 'vxlan':"", 'vlan':""},
    'd_test-net22':  {'name':"test-net22", 'Validation':"false", 'NetworkType':"",        'namespace':"default",    'host_if':"", 'rt_tables':"29", 'routes':"", 'vxlan':"16777215", 'vlan':""},
    }

cpu_pooling_pod1 = dict(obj_type="pod", obj_name="cpu-pooling-1", namespace="default", obj_count="1")
cpu_pooling_pod2 = dict(obj_type="pod", obj_name="cpu-pooling-2", namespace="default", obj_count="1")
cpu_pooling_pod3 = dict(obj_type="pod", obj_name="cpu-pooling-3", namespace="default", obj_count="1")
cpu_pooling_pod4 = dict(obj_type="pod", obj_name="cpu-pooling-4", namespace="default", obj_count="1")
cpu_pooling_pod5 = dict(obj_type="pod", obj_name="cpu-pooling-5", namespace="default", obj_count="1")
cpu_pooling_pod6 = dict(obj_type="pod", obj_name="cpu-pooling-6", namespace="default", obj_count="1")
cpu_pooling_pod7 = dict(obj_type="pod", obj_name="cpu-pooling-7", namespace="default", obj_count="1")
cpu_pooling_pod8 = dict(obj_type="pod", obj_name="cpu-pooling-8", namespace="default", obj_count="1")
cpu_pooling_pod9 = dict(obj_type="replicaset", obj_name="cpu-pooling-9", namespace="default", obj_count="1")
cpu_pooling_pod10 = dict(obj_type="replicaset", obj_name="cpu-pooling-10", namespace="default", obj_count="1")
cpu_pooling_pod11 = dict(obj_type="replicaset", obj_name="cpu-pooling-11", namespace="default", obj_count="1")

cpu_pooling_setter = dict(obj_type="pod", obj_name="cpu-setter", namespace="kube-system", obj_count="1")

cpu_pooling_cm_name = "cpu-pooler-configmap"

clusternetworks_properties = {
    'cnet_01': {'name': 'cnet-01', 'NetworkType': 'ipvlan', 'host_if': '', 'iface_type': 'ext'},
    'cnet_02': {'name': 'cnet-02', 'NetworkType': 'ipvlan', 'host_if': 'cnet02.502', 'iface_type': 'ext'},
    'cnet_03': {'name': 'cnet-03', 'NetworkType': 'ipvlan', 'host_if': 'vx_cnet03', 'iface_type': 'int'},
    'cnet_04': {'name': 'cnet-04', 'NetworkType': 'ipvlan', 'host_if': 'cnet04.504', 'iface_type': 'ext'},
    'cnet_05': {'name': 'cnet-05', 'NetworkType': 'ipvlan', 'host_if': '', 'iface_type': 'ext'},
    'cnet_06': {'name': 'cnet-06', 'NetworkType': 'ipvlan', 'host_if': 'cnet06.506', 'iface_type': 'ext'},
    'cnet_07': {'name': 'cnet-07', 'NetworkType': 'ipvlan', 'host_if': '', 'iface_type': 'int'},
    'cnet_08': {'name': 'cnet-08', 'NetworkType': 'ipvlan', 'host_if': '', 'iface_type': ''},
    'cnet_09': {'name': 'cnet-09', 'NetworkType': 'ipvlan', 'host_if': '', 'iface_type': ''},
}

clusternetworks_error_properties = {
    'cnet_invalid_01':    {'name': 'cnet-invalid-01'},
    'cnet_invalid_02_01': {'name': 'cnet-invalid-02-01'},
    'cnet_invalid_02_02': {'name': 'cnet-invalid-02-02'},
    'cnet_invalid_03':    {'name': 'cnet-invalid-03'},
    'cnet_invalid_04_01': {'name': 'cnet-invalid-04-01'},
    'cnet_invalid_04_02': {'name': 'cnet-invalid-04-02'},
    'cnet_invalid_05':    {'name': 'cnet-invalid-05'},
    'cnet_invalid_06':    {'name': 'cnet-invalid-06'},
    'cnet_invalid_07':    {'name': 'cnet-invalid-07'},
    'cnet_invalid_08':    {'name': 'cnet-invalid-08'},
    'cnet_invalid_09':    {'name': 'cnet-invalid-09'},
    'cnet_invalid_10':    {'name': 'cnet-invalid-10'},
    'cnet_invalid_11':    {'name': 'cnet-invalid-11'},
    'cnet_invalid_12':    {'name': 'cnet-invalid-12'},
}

tenantconfig_properties = {
    'tconf_01': {'name': "tconf-01"},
    'tconf_02': {'name': "tconf-02"},
    'tconf_03': {'name': "tconf-03"},
    'tconf_04': {'name': "tconf-04"},
    'tconf_05': {'name': "tconf-05"},
    'tconf_06': {'name': "tconf-06"},
    'tconf_07': {'name': "tconf-07"},
    'tconf_08': {'name': "tconf-08"},
}

tenantconfig_error_properties = {
    'tconf_invalid_01': {'name':"tconf-invalid-01"},
    'tconf_invalid_02': {'name':"tconf-invalid-02"},
    'tconf_invalid_03': {'name':"tconf-invalid-03"},
    'tconf_invalid_04': {'name':"tconf-invalid-04"},
    'tconf_invalid_05': {'name':"tconf-invalid-05"},
    'tconf_invalid_06': {'name':"tconf-invalid-06"},
    'tconf_invalid_07': {'name':"tconf-invalid-07"},
    'tconf_invalid_08': {'name':"tconf-invalid-08"},
    'tconf_invalid_09': {'name':"tconf-invalid-09"},
}

tenantnetwork_properties = {
    'tennet_01': {'name': "tennet-01", 'NetworkType': 'ipvlan', 'host_if': 'vx_tnet',     'iface_type': 'ext'},
    'tennet_02': {'name': "tennet-02", 'NetworkType': 'ipvlan', 'host_if': 'tnet02.1000', 'iface_type': 'int'},
    'tennet_03': {'name': "tennet-03", 'NetworkType': 'ipvlan', 'host_if': 'tnet03.1001', 'iface_type': 'int'},
    'tennet_04': {'name': "tennet-04", 'NetworkType': 'ipvlan', 'host_if': 'tnet04.2000', 'iface_type': 'storage'},
    'tennet_05': {'name': "tennet-05", 'NetworkType': 'ipvlan', 'host_if': 'tnet05.1002', 'iface_type': 'int'},
    'tennet_06': {'name': "tennet-06", 'NetworkType': 'ipvlan', 'host_if': 'tnet06.1003', 'iface_type': 'int'},
}

tenantnetwork_error_properties = {
    'tennet_invalid_01':     {'name': 'tennet-invalid-01'},
    'tennet_invalid_02':     {'name': 'tennet-invalid-02'},
    'tennet_invalid_03_01':  {'name': 'tennet-invalid-03-01'},
    'tennet_invalid_03_02':  {'name': 'tennet-invalid-03-02'},
    'tennet_invalid_04_01':  {'name': 'tennet-invalid-04-01'},
    'tennet_invalid_04_02':  {'name': 'tennet-invalid-04-02'},
    'tennet_invalid_05':     {'name': 'tennet-invalid-05'},
    'tennet_invalid_06':     {'name': 'tennet-invalid-06'},
    'tennet_invalid_07_01':  {'name': 'tennet-invalid-07-01'},
    'tennet_invalid_07_02':  {'name': 'tennet-invalid-07-02'},
    'tennet_invalid_08':     {'name': 'tennet-invalid-08'},
    'tennet_invalid_09':     {'name': 'tennet-invalid-09'},
    'tennet_invalid_10':     {'name': 'tennet-invalid-10'},
    'tennet_invalid_11':     {'name': 'tennet-invalid-11'},
}

network_attach_properties = {
    'cnet_pod1': {'name': 'cnet-pod1', 'NetworkType': 'ipvlan', 'host_if': 'vx_cnet-pod1', 'routes':"10.0.0.0/32: 10.5.1.1"},
    'cnet_pod2': {'name': 'cnet-pod2', 'NetworkType': 'ipvlan', 'host_if': 'vx_cnet-pod2'},
    'cnet_pod3': {'name': 'cnet-pod3', 'NetworkType': 'ipvlan', 'host_if': 'vx_cnet-pod3'},
    'cnet_pod4': {'name': 'cnet-pod4', 'NetworkType': 'ipvlan', 'host_if': 'vx_cnet-pod4'},
    'cnet_pod5': {'name': 'cnet-pod5', 'NetworkType': 'ipvlan', 'host_if': ''},
    'cnet_pod6': {'name': 'cnet-pod6', 'NetworkType': 'ipvlan', 'host_if': 'vx_cnet-pod6'},
    'cnet_pod7': {'name': 'cnet-pod7', 'NetworkType': 'ipvlan', 'host_if': 'vx_cnet-pod7'},
}

tenantnetwork_attach_properties = {
    'tennet_attach_01': {'name': 'tennet-attach-01', 'namespace': 'default',     'NetworkType': 'ipvlan', 'host_if': '', 'routes': "10.10.1.0/24: 10.240.1.100"},
    'tennet_attach_02': {'name': 'tennet-attach-02', 'namespace': 'kube-system', 'NetworkType': 'ipvlan', 'host_if': '', 'routes':"10.10.2.0/24: 10.240.2.1"},
    'tennet_attach_03': {'name': 'tennet-attach-03', 'namespace': 'default',     'NetworkType': 'ipvlan', 'host_if': ''},
    'tennet_attach_04': {'name': 'tennet-attach-04', 'namespace': 'default',     'NetworkType': 'ipvlan', 'host_if': '', 'flannel_pool': {'start': '10.244.0.1', 'end': '10.244.255.254'}},
    'tennet_attach_05': {'name': 'tennet-attach-05', 'namespace': 'default',     'NetworkType': 'ipvlan', 'host_if': ''},
    'tennet_attach_06': {'name': 'tennet-attach-06', 'namespace': 'default',     'NetworkType': 'ipvlan', 'host_if': ''},
    'tennet_attach_07': {'name': 'tennet-attach-07', 'namespace': 'default',     'NetworkType': 'ipvlan', 'host_if': ''},
}


tennet_pod1  = dict(obj_type="pod", obj_name="tennet-pod-01", obj_count="4", namespace="default",     ip_list=["10.240.1.1", "10.240.1.8", "10.240.1.9", "10.240.1.254"])
tennet_pod2  = dict(obj_type="pod", obj_name="tennet-pod-02", obj_count="4", namespace="default",     ip_list=["10.240.1.2", "10.240.1.3", "10.240.1.4", "10.240.1.5", "10.240.1.6", "10.240.1.7"])
tennet_pod3  = dict(obj_type="pod", obj_name="tennet-pod-03", obj_count="4", namespace="default",     ip_list=["10.240.1.1", "10.240.1.8", "10.240.1.9", "10.240.1.254"])
tennet_pod4  = dict(obj_type="pod", obj_name="tennet-pod-04", obj_count="5", namespace="kube-system", ip_list=["10.240.2.2", "10.240.2.3", "10.240.2.4", "10.240.2.5", "10.240.2.6"])
tennet_pod5  = dict(obj_type="pod", obj_name="tennet-pod-05", obj_count="1", namespace="kube-system", ip_list=[])
tennet_pod6  = dict(obj_type="pod", obj_name="tennet-pod-06", obj_count="4", namespace="default",     ip_list=[])
tennet_pod7  = dict(obj_type="pod", obj_name="tennet-pod-07", obj_count="5", namespace="default",     ip_list=[])
tennet_pod8  = dict(obj_type="pod", obj_name="tennet-pod-08", obj_count="1", namespace="default",     ip_list=[])
tennet_pod9  = dict(obj_type="pod", obj_name="tennet-pod-09", obj_count="2", namespace="default",     ip_list=[])
tennet_pod10 = dict(obj_type="pod", obj_name="tennet-pod-10", obj_count="1", namespace="default",     ip_list=[])
tennet_pod11 = dict(obj_type="pod", obj_name="tennet-pod-11", obj_count="1", namespace="default",     ip_list=[])
tennet_pod12 = dict(obj_type="pod", obj_name="tennet-pod-12", obj_count="1", namespace="default",     ip_list=["10.20.5.101", "10.240.1.1"])
tennet_pod13 = dict(obj_type="pod", obj_name="tennet-pod-13", obj_count="1", namespace="default",     ip_list=[])
tennet_pod14 = dict(obj_type="pod", obj_name="tennet-pod-14", obj_count="1", namespace="default",     ip_list=["10.20.6.10", "10.240.1.5", "10.20.5.100"])
