#!/usr/bin/env python

import tempfile
import requests
import re
import sys
import os
import time
import subprocess
import shutil
from contextlib import contextmanager

ACCOUNT_ID_MATCHER = re.compile("Account ID: (.+)")
ACCOUNT_SECRET_MATCHER = re.compile("Account secret: (.+)")

@contextmanager
def server(env):
    """
    Context manager for running the server. This starts the server up, waits
    until its responsive, then yields. When the context manager's execution is
    resumed, it kills the server.
    """

    # Start the process
    server_proc = subprocess.Popen(["indradb-server"], stdout=sys.stdout, stderr=sys.stderr, env=env)
    
    while True:
        # Check if the server is now responding to HTTP requests
        try:
            res = requests.get("http://localhost:8000", timeout=1)

            if res.status_code == 401:
                break
        except requests.exceptions.RequestException:
            pass

        # Server is not yet responding to HTTP requests - let's make sure it's
        # running in the first place
        if server_proc.poll() != None:
            raise Exception("Server failed to start")

        time.sleep(1)

    try:
        yield
    finally:
        server_proc.terminate()

def create_account(env):
    """Creates an IndraDB account"""
    create_user_proc = subprocess.Popen(["indradb-account", "add"], env=env, stdout=subprocess.PIPE, stderr=sys.stderr)
    create_user_output, _ = create_user_proc.communicate()
    create_user_output_str = create_user_output.decode("utf-8")
    account_id = ACCOUNT_ID_MATCHER.search(create_user_output_str).groups()[0]
    secret = ACCOUNT_SECRET_MATCHER.search(create_user_output_str).groups()[0]
    return account_id, secret

def run(rdb_dir):
    env = dict(os.environ)

    env.update({
        "RUST_BACKTRACE": "1",
        "DATABASE_URL": "rocksdb://%s" % rdb_dir,
        "INDRADB_SCRIPT_ROOT": "%s/test_scripts" % os.getcwd(),
        "INDRADB_HOST": "localhost:8000",
    })

    account_id, secret = create_account(env)

    with server(env):
        env.update({
            "INDRADB_ACCOUNT_ID": account_id,
            "INDRADB_SECRET": secret,
        })

        proc = subprocess.Popen(
            ["nosetests", "indradb.test"],
            stdout=sys.stdout,
            stderr=sys.stderr,
            env=env
        )

        return proc.wait()
    
    raise Exception("This code path should not get hit")

def main():
    temp_dir = tempfile.mkdtemp("indradb-python-client")
    return_code = -1
    
    try:
        return_code = run(temp_dir)
    finally:
        shutil.rmtree(temp_dir)

    sys.exit(return_code)

if __name__ == "__main__":
    main()
