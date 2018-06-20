#!/usr/bin/env python

import sys
import os
import time
import socket
import subprocess
from contextlib import contextmanager

from indradb import Client

PORT = 27615
HOST = "localhost:%s" % PORT

@contextmanager
def server(env):
    """
    Context manager for running the server. This starts the server up, waits
    until its responsive, then yields. When the context manager's execution is
    resumed, it kills the server.
    """

    # Start the process
    server_proc = subprocess.Popen(["indradb"], stdout=sys.stdout, stderr=sys.stderr, env=env)
    
    while True:
        try:
            client = Client(HOST)
            
            if client.ping().wait().ready:
                break
        except socket.error as e:
            print(e)

        # Server is not yet responding to requests - let's make sure it's
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
        "PORT": str(PORT),
        "RUST_BACKTRACE": "1",
        "DATABASE_URL": "memory://",
        "INDRADB_HOST": HOST
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
