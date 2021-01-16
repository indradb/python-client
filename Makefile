.PHONY: init release test

venv:
	virtualenv -p python3 venv
	. venv/bin/activate && pip install tox nose pdoc grpcio==1.27.2 grpcio-tools==1.27.2

init: venv
	git submodule update --init --recursive
	. venv/bin/activate && python3 -m grpc_tools.protoc -I./indradb_server/proto \
		--python_out=indradb --grpc_python_out=indradb indradb.proto
	# fix import
	sed -i -e 's/import indradb_pb2/import indradb.indradb_pb2/g' indradb/indradb_pb2_grpc.py

doc:
	. venv/bin/activate && python setup.py clean build install
	. venv/bin/activate && pdoc --html --html-dir ./doc ./indradb

release:
	git checkout master
	git push origin master
	rm -rf build dist
	python setup.py clean build sdist bdist_wheel
	. venv/bin/activate && twine upload --skip-existing dist/*

test:
	. venv/bin/activate && tox
