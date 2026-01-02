import sysconfig

from setuptools import setup, Extension
import numpy as np



def main() -> None:
    base_nvidia_packages_dir = f'{sysconfig.get_paths()["purelib"]}/nvidia'

    setup(ext_modules=[
        Extension(name='app.fast',
                  sources=[
                      'src/cpp/fast/fast.cpp'
                  ],
                  include_dirs=[
                      np.get_include(),
                      f'{base_nvidia_packages_dir}/nvjpeg/include',
                      f'{base_nvidia_packages_dir}/cuda_runtime/include',
                      f'{base_nvidia_packages_dir}/cuda_nvcc/include'
                  ],
                  library_dirs=[
                      f'{base_nvidia_packages_dir}/nvjpeg/lib',
                      f'{base_nvidia_packages_dir}/cuda_runtime/lib',
                      f'{base_nvidia_packages_dir}/cuda_nvcc/lib'
                  ],
                  extra_link_args=[
                      f'{base_nvidia_packages_dir}/cuda_runtime/lib/libcudart.so.12',
                      f'{base_nvidia_packages_dir}/nvjpeg/lib/libnvjpeg.so.12',

                  ],
                  runtime_library_dirs=[
                      f'{base_nvidia_packages_dir}/nvjpeg/lib',
                      f'{base_nvidia_packages_dir}/cuda_runtime/lib',
                      f'{base_nvidia_packages_dir}/cuda_nvcc/lib'
                  ],
                  extra_compile_args=[
                      '-Wall',
                      '-Wextra',
                      '-Wno-unused-parameter'
                  ],
                  language='c++'),
    ])

if __name__ == '__main__':
    main()
