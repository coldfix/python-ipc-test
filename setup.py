from setuptools import setup

setup(
    name='python-ipc-test',
    version='0.0.0',
    description='Demonstration and benchmark of multiple variations to set up IPC with a subprocess.',
    packages=['ipctest',
              'ipctest.connection',
              'ipctest.protocol'],
    install_requires=['docopt',
                      'numpy',
                      'matplotlib'],
)

