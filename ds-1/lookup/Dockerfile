#
# Simple backend demo server image
#

FROM ghcr.io/maxotta/kiv-ds-docker:latest

RUN yum -q -y install python3

COPY . /opt/lookup

RUN pip3 install -r /opt/lookup/requirements.txt

CMD /usr/bin/python3 /opt/lookup/src/main.py

# EOF
