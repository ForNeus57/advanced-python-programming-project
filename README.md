# CPython-based Extention for Image Manipulation

### Team members:
- Konrad Bodzioch
- Dominik Breksa
- Miłosz Góralczyk

-------------

## Project Overview

This repository contains our efforts for creating a Python based C extention image enhance library. As the first part of the project a python-compatibile library will be implemented, containing various functionalities from the area of Image Processing and Manipulation.

The calculations are going to be performed within c++ code, with the extention bridging the gap between languages, allowing for full acces within the Python environment while utilizing the computational speed of low-level language.

Further on, we plan on displaying the capabilities of developed extension with a python-based User Interface or Pipeline for Image Manipulation and  Image Processing, allowing user to utilize the functionalities from the level of a command line or a Graphic Interface Upload-Manipulate-Output tool.

-------------

## Used tools and dependencies

The project requires:

- Python 3.13
- CPython implementation

```bash
pip3 install -e .
```
 will install following packages for end user:

numpy 2.3.5

```bash
pip3 install -e .[developement]
```

```txt
  mypy==1.18.2,
  ruff==0.14.6,
  flake8==7.3.0,
  pylint==4.0.2,
  nbqa==1.9.1
  pytest==9.0.1
```

-------------
