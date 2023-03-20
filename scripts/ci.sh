#!/bin/bash

set -ex

# install protobuf
sudo apt-get install protobuf-compiler
# install python deps
pip install -r requirements.txt
