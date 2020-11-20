# -*- coding: utf-8 -*-
from setuptools import setup

with open('README.md') as file:
    readme = file.read()

with open('LICENSE') as legal:
    license = legal.read()

setup(
    name='SMPG-Project',
    packages=['test', 'source', 'source.image'],
    entry_points={'console_scripts': ['runfile = source.build:main']},
    version='1.2.5',
    description='This is a rainfall forecast generator & analysis tool',
    long_description=readme,
    author='Jeaustin Sirias Chacón',
    author_email='jeaustin.sirias@ucr.ac.cr',
    url='https://github.com/JeaustinSirias/Seasonal_Monitoring_Probability_Generator',
    license=license,
    include_package_data=True,
)
 
