# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

#with open('README.rst') as f:
#    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

setup(
    name='Seasonal Monitoring Probability Generator',
    version='1.2.0',
    description='This is a rainfall forecast generator tool',
    long_description=readme,
    author='Jeaustin Sirias',
    author_email='jeaustin.sirias@ucr.ac.cr',
    url='https://github.com/JeaustinSirias/Seasonal_Monitoring_Probability_Generator',
    license=license,
    packages=find_packages(exclude=('test', 'docs'))
)
