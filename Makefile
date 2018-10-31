.PHONY: init release test

init:
	virtualenv --no-site-packages venv
	. venv/bin/activate && pip install tox nose pdoc
	git submodule update --init --recursive
	cp indradb_server/bin/indradb.capnp indradb/

doc:
	. venv/bin/activate && python setup.py clean build install
	. venv/bin/activate && pdoc --html --html-dir ./doc ./indradb

release:
	git checkout master
	git push origin master
	python setup.py clean build sdist upload

test:
	. venv/bin/activate && tox
