#!/bin/bash

# Download and install Pig
PIG_VERSION=0.17.0
curl -O https://dlcdn.apache.org/pig/pig-${PIG_VERSION}/pig-${PIG_VERSION}.tar.gz
tar -xzf pig-${PIG_VERSION}.tar.gz -C /opt
mv /opt/pig-${PIG_VERSION} /opt/pig
rm pig-${PIG_VERSION}.tar.gz

# Set environment variables
echo "export PIG_HOME=/opt/pig" >> /root/.bashrc
echo "export PATH=\$PATH:/opt/pig/bin" >> /root/.bashrc

source /root/.bashrc

echo "Pig installed successfully."
