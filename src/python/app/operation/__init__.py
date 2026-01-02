"""Module providing import convenience for operations"""

from app.operation.bgr2rgb import BGR2RGB
from app.operation.flip import Flip
from app.operation.grayscale import Grayscale
from app.operation.histogram_equalization import HistogramEqualization
from app.operation.identity import Identity
from app.operation.ioperation import IOperation
from app.operation.roll import Roll
from app.operation.rotate90 import Rotate90

__all__ = [BGR2RGB.__name__,
           Flip.__name__,
           Grayscale.__name__,
           HistogramEqualization.__name__,
           Identity.__name__,
           IOperation.__name__,
           Roll.__name__,
           Rotate90.__name__]
