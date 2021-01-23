#!/usr/bin/env python3

import sys
import os
import time
import socket
import subprocess
import os
from contextlib import contextmanager

from indradb import Client

HOST = "localhost:27615"

@contextmanager
def server(env):
    """
    Context manager for running the server. This starts the server up, waits
    until its responsive, then yields. When the context manager's execution is
    resumed, it kills the server.
    """

    # Start the process
    server_proc = subprocess.Popen(
        ["cargo", "run"],
        cwd=os.path.join(".", "indradb_server", "bin"),
        stdout=sys.stdout,
        stderr=sys.stderr,
        env=env
    )
    
    while True:
        try:
            Client(HOST).ping()
            break
        except:
            print("server not yet ready")

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
        "RUST_BACKTRACE": "1",
        "DATABASE_URL": "memory://",
        "INDRADB_HOST": HOST
    })

    with server(env):
        subprocess.run(
            ["nosetests", "indradb.test", *sys.argv[1:]],
            env=env,
            check=True,
        )

if __name__ == "__main__":
    main()
