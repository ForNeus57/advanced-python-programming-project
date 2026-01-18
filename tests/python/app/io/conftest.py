from pathlib import Path

import pytest


@pytest.fixture(params=['1.bmp', '2.bmp', '3.bmp', '4.bmp'], scope="function")
def resource_bmp(request, resource_path: Path):
    with open(resource_path / request.param, mode='rb') as f:
        yield f

@pytest.fixture(params=['1.png', '2.png', '3.png', '3_cat.png', '4.png'], scope="function")
def resource_png(request, resource_path: Path):
    with open(resource_path / request.param, mode='rb') as f:
        yield f

@pytest.fixture(params=['3.jpg'], scope="function")
def resource_jpg(request, resource_path: Path):
    with open(resource_path / request.param, mode='rb') as f:
        yield f

@pytest.fixture(params=['4.avif'], scope="function")
def resource_avif(request, resource_path: Path):
    with open(resource_path / request.param, mode='rb') as f:
        yield f
