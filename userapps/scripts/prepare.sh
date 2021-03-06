#!/usr/bin/env bash

if [ -d /tmp/venv ]; then
exit 0
fi

apt-get update
apt-get -y install git python-pip virtualenv python-dev

cd /tmp
mkdir venv
cd venv
virtualenv --no-setuptools .

cd /tmp
git clone http://github.com/openstack/oslo.messaging
source venv/bin/activate
pip install setuptools
pip install eventlet PyYAML oslo.messaging petname redis zmq pika_pool
cd oslo.messaging
pip install .