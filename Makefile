.PHONY: init release test

init:
	virtualenv --no-site-packages venv
	. venv/bin/activate && pip install tox nose pdoc
	git submodule update --init --recursive
	make indradb/indradb.capnp

indradb/indradb.capnp:
	cp indradb_server/bin/indradb.capnp indradb/

doc:
	. venv/bin/activate && python setup.py clean build install
	. venv/bin/activate && pdoc --html --html-dir ./doc ./indradb

release:
	git checkout master
	git push origin master
	python setup.py clean build sdist bdist_wheel
	. venv/bin/activate && twine upload --skip-existing dist/*

test:
	. venv/bin/activate && tox
