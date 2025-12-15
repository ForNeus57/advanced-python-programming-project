"""Module implementing the image class used in the operations"""

from dataclasses import dataclass
from typing import final

import numpy as np


@final
@dataclass(slots=True)
class Image:
    """Class that stores the image object as a numpy array"""

    data: np.ndarray
