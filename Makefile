.PHONY: init release test

init: venv indradb_server/Cargo.toml indradb/indradb.capnp

venv:
	virtualenv --no-site-packages venv
	source venv/bin/activate && pip install tox nose pdoc

indradb_server/Cargo.toml:
	git submodule update --init --recursive
	cd indradb_server/bin && cargo build

indradb/indradb.capnp: indradb_server/Cargo.toml
	cp indradb_server/bin/indradb.capnp indradb/

doc: venv
	source venv/bin/activate && python setup.py clean build install
	source venv/bin/activate && pdoc --html --html-dir ./doc ./indradb

release:
	git checkout master
	git push origin master
	python setup.py clean build sdist upload

test: venv indradb_server/target
	tox
