from setuptools import setup
from setuptools import find_namespace_packages

#load the README file
with open(file='README.md', mode='r') as fh:
    long_description = fh.read()

setup(
    name = 'attacker-2024',
    author = 'Stack OverFlow',
    description= 'a trading rebot built for Python that uses the Yuanta API',
    long_description=long_description,
    long_description_content_type = 'text/markdown',
    url = '',
    install_requirement = [],
    
)