from dataclasses import dataclass
from typing import final

import numpy as np


@final
@dataclass(slots=True)
class Image:
    data: np.ndarray
