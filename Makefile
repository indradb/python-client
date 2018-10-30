.PHONY: release test

doc:
	PYTHONPATH=.:$(PYTHONPATH) pdoc --html --html-dir ./doc ./indradb

release:
	git checkout master
	git push origin master
	python setup.py clean build sdist upload

venv:
	virtualenv --no-site-packages venv
	source venv/bin/activate && pip install tox nose

indradb_server/Cargo.toml:
	git submodule update --init --recursive

indradb_server/target: indradb_server/Cargo.toml
	cd indradb_server/bin && cargo build

test: venv indradb_server/target
	tox
