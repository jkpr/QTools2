from distutils.core import setup

setup(
    name='qtools2',
    version='0.1.5',
    author='James K. Pringle',
    author_email='jpringle@jhu.edu',
    url='https://github.com/jkpr/QTools2',
    packages=[
        'qtools2', 
        'qtools2.test'
    ],
    license='LICENSE.txt',
    description='Useful tools for working with PMA2020 Questionnaires',
    long_description=open('README.txt').read(),
    install_requires=[
        'pmaxform>=1.0.1'
    ],
    dependency_links=[
        'https://github.com/jkpr/pmaxform/zipball/master#egg=pmaxform-1.0.1'
    ]
)
