# IndraDB python client [![Build Status](https://travis-ci.org/indradb/python-client.svg?branch=master)](https://travis-ci.org/indradb/python-client)

IndraDB's python client, which uses the REST API to enable graph queries and manipulation from python code.

See the [api doc](https://htmlpreview.github.io/?https://github.com/indradb/python-client/blob/develop/doc/indradb/index.html) for more info.

## Tests

To run tests, ensure you have the IndraDB applications in your `PATH`, then run:

```bash
virtualenv --no-site-packages venv
source venv/bin/activate && pip install tox nose requests
tox
```
