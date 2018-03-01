.PHONY: release

doc:
	PYTHONPATH=.:$(PYTHONPATH) pdoc --html --html-dir ./doc ./indradb

release:
	git checkout master
	git push origin master
	python setup.py clean build sdist upload
