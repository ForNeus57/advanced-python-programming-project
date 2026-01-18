from pathlib import Path
from typing import Any, Generator

import pytest

@pytest.fixture
def resource_path() -> Generator[Path, Any, None]:
    yield Path(__file__).parent.parent.parent / 'resources'
