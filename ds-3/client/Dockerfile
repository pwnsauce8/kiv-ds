#
# Zookeeper client node demo container image
#

FROM ghcr.io/maxotta/kiv-ds-docker:latest

RUN yum -q -y install python3
# RUN pip3 install kazoo

COPY . /opt/client

RUN pip3 install -r /opt/client/requirements.txt

CMD /usr/bin/python3 /opt/client/python/client.py

# EOF
