# braid python client [![Build Status](https://travis-ci.org/braidery/python-client.svg?branch=master)](https://travis-ci.org/braidery/python-client)

Braid's python client, which uses the REST API to enable graph queries and manipulation from python code.

See the [api doc](https://braidery.github.io/apis/python-client/braid/index.html) for more info.

## Tests

To run tests, ensure you have the braid applications in your `PATH`, then run:

```bash
virtualenv --no-site-packages venv
source venv/bin/activate && pip install tox nose requests
tox
```
