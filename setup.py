from setuptools import setup, Extension
import numpy

def main() -> None:
    setup(ext_modules=[
        Extension('app.fast', ['src/app/fast/foo.c'], include_dirs=[numpy.get_include()])
    ])


if __name__ == '__main__':
    main()


# {'stdlib': '/Library/Frameworks/Python.framework/Versions/3.13/lib/python3.13', 
#  'platstdlib': '/Users/bodzio/Desktop/APP/advanced-python-programming-project/.venv/lib/python3.13', 
#  'purelib': '/Users/bodzio/Desktop/APP/advanced-python-programming-project/.venv/lib/python3.13/site-packages', 
#  'platlib': '/Users/bodzio/Desktop/APP/advanced-python-programming-project/.venv/lib/python3.13/site-packages', 
#  'include': '/Library/Frameworks/Python.framework/Versions/3.13/include/python3.13', 
#  'platinclude': '/Library/Frameworks/Python.framework/Versions/3.13/include/python3.13', 
#  'scripts': '/Users/bodzio/Desktop/APP/advanced-python-programming-project/.venv/bin', 
#  'data': '/Users/bodzio/Desktop/APP/advanced-python-programming-project/.venv'}