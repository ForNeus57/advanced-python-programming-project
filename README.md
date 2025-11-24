# CPython-based Extension for Image Manipulation

<!-- TOC -->
* [CPython-based Extension for Image Manipulation](#cpython-based-extension-for-image-manipulation)
    * [Team members](#team-members)
  * [Project Overview](#project-overview)
  * [Used tools and dependencies](#used-tools-and-dependencies)
    * [Installation Guide](#installation-guide)
      * [Prerequisites](#prerequisites)
      * [End user package installation:](#end-user-package-installation)

    * [Dependencies](#dependencies)
<!-- TOC -->

### Team members

- Konrad Bodzioch
- Dominik Breksa
- Miłosz Góralczyk

-------------

## Project Overview

This repository contains our efforts for creating a Python based C extension image enhance library. As the first part of the project, a python-compatible library will be implemented, containing various functionalities from the area of Image Processing and Manipulation.

The calculations are going to be performed within c++ code, with the extension bridging the gap between languages, allowing for full access within the Python environment while utilising the computational speed of low-level language.

Further on, we plan on displaying the capabilities of developed extension with a python-based User Interface or Pipeline for Image Manipulation and  Image Processing, allowing user to utilise the functionalities from the level of a command line or a Graphic Interface Upload-Manipulate-Output tool.

-------------

## Used tools and dependencies

The project contains the `app` python package. Short for Advanced-Python-Programming.

The package requires the following configuration in order to be properly installed (see later sections):

- Python 3.13
- CPython implementation
- numpy 2.3.5

### Installation Guide

The package can be installed with two dependencies bundles:
- baseline package dependencies intended for end user.
- development dependencies used to test, build the project (requires additional installations).

Our package uses the `setuptools` backend.

#### Prerequisites

Create python environment using `venv`:

```bash
python3 -m venv .venv
```

Next, you need to choose one of the dependencies bundles.

#### End user package installation:

Run the following commands in your terminal and install the `app` package:

```bash
pip3 install -e .
```

Alternatively previous step  can be accomplished using by running the `Makefile` command:

```bash
make python-install
```

####
Package with development dependencies installation:

```bash
pip3 install -e .[developement]
```

It is not needed to install the package in editable mode (`-e` flag).
However, if one would want to do code modification, the option is very helpful.

And using makefile:

```bash
make python-install-editable
```

### Dependencies

See also `setup.cfg` for more details.

```txt
mypy==1.18.2,
ruff==0.14.6,
flake8==7.3.0,
pylint==4.0.2,
nbqa==1.9.1
pytest==9.0.1
```

-------------
