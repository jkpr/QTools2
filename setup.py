from distutils.core import setup

from qtools2 import __version__

setup(
    name='qtools2',
    version=__version__,
    author='James K. Pringle',
    author_email='jpringle@jhu.edu',
    url='https://github.com/jkpr/QTools2',
    packages=[
        'qtools2', 
        'qtools2.test'
    ],
    license='LICENSE.txt',
    description='Useful tools for working with PMA2020 Questionnaires',
    long_description=open('README.rst').read(),
    install_requires=[
        'pmaxform>=1.0.1'
    ],
)
