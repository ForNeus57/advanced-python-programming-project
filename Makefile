all:
	echo 'All'

python-install:
	pip3 install .

python-install-development:
	pip3 install .[development]

python-install-editable:
	pip3 install -e .[development]

mypy:
	mypy ./src/python/

ruff:
	ruff check ./src/python/

flake8:
	flake8 ./src/python/

