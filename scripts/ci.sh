#!/bin/bash

set -ex

rust_variant=$1
os=$2

# install protobuf
if [ "$os" == "ubuntu-latest" ]; then
    eval "$(/home/linuxbrew/.linuxbrew/bin/brew shellenv)"
fi
brew install protobuf
