# braid python client [![Build Status](https://travis-ci.org/braidery/python-client.svg?branch=master)](https://travis-ci.org/braidery/python-client)

Braid's python client, which uses the REST API to enable graph queries and manipulation from python code.

At the moment this only works on python 3. Pull requests to support python 2 gladly accepted!

## Tests

To run tests:

```bash
virtualenv --no-site-packages -p python3
source venv/bin/activate
pip install requests iso8601
PATH=path/to/braid/apps:$PATH ./test.py
```
