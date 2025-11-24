all:
	echo 'All'

python-install:
	pip3 install .

python-install-editable:
	pip3 install -e .[development]