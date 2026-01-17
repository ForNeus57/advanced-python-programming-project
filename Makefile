.PHONY: all python-install python-install-development python-install-editable clang-format clang-tidy mypy ruff flake8 pylint pytest pytest-coverage


all: clang-tidy mypy ruff flake8 pylint pytest-coverage
	echo 'All'

python-install:
	pip3 install cuda-toolkit[cudart,nvcc,nvjpeg]==12.4.1
	pip3 install .

python-install-development:
	pip3 install cuda-toolkit[cudart,nvcc,nvjpeg]==12.4.1
	pip3 install .[development]

python-install-editable:
	pip3 install cuda-toolkit[cudart,nvcc,nvjpeg]==12.4.1
	pip3 install -e .[development]

clang-format:
	 clang-format -i $(shell find ./src/cpp/ -name '*.hpp' -o -name '*.cpp')

clang-tidy:
	clang-tidy $(shell find ./src/cpp/ -name '*.hpp' -o -name '*.cpp') -- -I$(shell python3 -c "import sysconfig; print(sysconfig.get_path('include'))") -I$(shell python3 -c "import numpy; print(numpy.get_include())") -I$(shell python3 -c "import sysconfig; print(f'{sysconfig.get_paths()['purelib']}/nvidia/nvjpeg/include')") -I$(shell python3 -c "import sysconfig; print(f'{sysconfig.get_paths()['purelib']}/nvidia/cuda_runtime/include')") -I$(shell python3 -c "import sysconfig; print(f'{sysconfig.get_paths()['purelib']}/nvidia/cuda_nvcc/include')")

mypy:
	mypy ./src/python/

ruff:
	ruff check ./src/python/

flake8:
	flake8 ./src/python/

pylint:
	pylint ./src/python/

pytest:
	pytest

pytest-coverage:
	coverage run -m pytest ./tests/python
	coverage report --show-missing