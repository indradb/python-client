#!/bin/bash

set -ex

# Use sed to replace the SSH URL with the public URL, then initialize
# submodules. This is done because TravisCI can't pull from the SSH
# URI. Via https://stackoverflow.com/questions/15674064/how-to-fix-a-permission-denied-publickey-error-for-a-git-submodule-update-in-t
sed -i 's/git@github.com:/https:\/\/github.com\//' .gitmodules
git submodule update --init --recursive

sudo apt-get -qq update
sudo apt-get install -y python3
make venv

source ~/.cargo/env || true
