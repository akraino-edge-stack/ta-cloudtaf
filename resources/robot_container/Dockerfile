FROM centos:7.6.1810
MAINTAINER Balint Tobik <balint.tobik@nokia.com> Endre Nemeth <endre.nemeth@nokia.com>

RUN yum -y install https://dl.fedoraproject.org/pub/epel/epel-release-latest-7.noarch.rpm \
    && yum -y --setopt=skip_missing_names_on_install=False install \
      gcc \
      python-devel \
      python2-pip \
      openssh-clients \
      jq \
    && yum clean all

RUN pip install --upgrade pip \
    && pip install --upgrade setuptools \
    && pip install PyYAML \
    && pip install ruamel.yaml \
    && pip install positional \
    && pip install pyparsing \
    && pip install netaddr \
    && pip install netifaces \
    && pip install robotframework==3.0.4 \
    && pip install robotframework-sshlibrary \
    && pip install paramiko==2.4.2 \
    && pip install requests \
    && pip install robotframework-pabot==0.44


COPY robot-deployment-test.sh /robot-deployment-test.sh
COPY testcases/ /cloudtaf/testcases/
COPY libraries/ /cloudtaf/libraries/
COPY resources/ /cloudtaf/resources/

ENTRYPOINT /robot-deployment-test.sh
