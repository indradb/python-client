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

            if res.status_code == 404:
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

def main():
    env = dict(os.environ)

    env.update({
        "RUST_BACKTRACE": "1",
        "DATABASE_URL": "memory://",
        "INDRADB_SCRIPT_ROOT": "%s/test_scripts" % os.getcwd(),
        "INDRADB_HOST": "localhost:8000",
    })

    with server(env):
        proc = subprocess.Popen(
            ["nosetests", "indradb.test"],
            stdout=sys.stdout,
            stderr=sys.stderr,
            env=env
        )

        sys.exit(proc.wait())
    
    raise Exception("This code path should not get hit")

if __name__ == "__main__":
    main()
