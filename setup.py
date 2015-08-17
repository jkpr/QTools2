from distutils.core import setup

setup(
    name='QTools2',
    version='0.1.1',
    author='James K. Pringle',
    author_email='jpringle@jhu.edu',
    url='http://www.pma2020.org',
    packages=[
        'qtools2', 
        'qtools2.test'
    ],
    license='LICENSE.txt',
    description='Useful tools for working with PMA2020 Questionnaires',
    long_description=open('README.txt').read(),
    install_requires=[
        'pyxform>=0.9.22'
    ],
)
