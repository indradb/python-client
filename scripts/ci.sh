#!/bin/bash

set -ex

# install protobuf
eval "$(/home/linuxbrew/.linuxbrew/bin/brew shellenv)"
brew install protobuf
# install python deps
pip install -r requirements.txt
