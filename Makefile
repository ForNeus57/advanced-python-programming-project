all:
	echo 'All'

python-install:
	pip3 install .

python-install-development:
	pip3 install .[development]

python-install-editable:
	pip3 install -e .[development]

clang-format:
	 clang-format -i $(shell find ./src/cpp/ -name '*.hpp' -o -name '*.cpp')

clang-tidy:
	clang-tidy $(shell find ./src/cpp/ -name '*.hpp' -o -name '*.cpp') -- -I$(shell python3 -c "import sysconfig; print(sysconfig.get_path('include'))") -I$(shell python3 -c "import numpy; print(numpy.get_include())")

mypy:
	mypy ./src/python/

ruff:
	ruff check ./src/python/

flake8:
	flake8 ./src/python/
