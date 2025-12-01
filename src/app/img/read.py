from pathlib import Path

import numpy as np

def read_bitmap_image(path: Path) -> np.ndarray:
    image_bytes = path.read_bytes()
    breakpoint()
