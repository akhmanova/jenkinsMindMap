#!/usr/bin/env bash


# Install Python
apt-get update && apt-get install -y --force-yes python

# Install Python requirements
apt-get update && apt-get install -y --force-yes python-pip
pip install -r requirements.txt

# Install wget
#apt-get update && apt-get install -y --force-yes wget

# Install ping
#apt-get update && apt-get install -y --force-yes iputils-ping

# Install Jenkins API
wget -q -O - https://pkg.jenkins.io/debian/jenkins-ci.org.key | apt-key add -
sh -c 'echo deb http://pkg.jenkins.io/debian-stable binary/ > /etc/apt/sources.list.d/jenkins.list'

# Install vim
#apt-get update && apt-get install -y --force-yes vim

# Install curl
#apt-get update && apt-get install -y --force-yes curl


mkdir /temp

touch /temp/mycsvfile.csv

python fun.py

pip uninstall -y -r requirements.txt

# Install Python
apt-get update && apt-get install -y --force-yes python

# Install Python requirements
apt-get update && apt-get install -y --force-yes python-pip

#SECOND
pip install -r requirements-second.txt


mkdir -p /temp/output


ls /opt/
python fun-second.py

cp -a /opt/* /temp/
