.PHONY: test full_test

test:
	pylint --disable=I --reports=no src/dantalian tests
	nosetests

full_test:
	pylint src/bloom tests
	nosetests --with-coverage --cover-package=bloom
