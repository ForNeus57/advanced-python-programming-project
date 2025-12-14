from setuptools import setup, Extension
import numpy as np

def main() -> None:
    setup(ext_modules=[
        Extension(name='app.fast',
                  sources=['src/cpp/fast/fast.cpp'],
                  include_dirs=[np.get_include()],
                  language='c++'),
    ])

if __name__ == '__main__':
    main()
