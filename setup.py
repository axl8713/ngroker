# -*- coding: utf-8 -*-

from setuptools import setup, find_packages


with open('README.md') as f:
    readme = f.read()

# with open('LICENSE') as f:
#     license = f.read()

setup(
    name='ngroker',
    version='0.1.0',
    description='Opens and publishes via a Telegram bot TCP or HTTP ngrok tunnels',
    long_description=readme,
    author='Alessandro Ricchiuti',
    author_email='ale.ricchiuti@hotmail.it',
    url='https://github.com/axl8713/ngroker',
    # license=license,
    packages=find_packages(exclude=('tests', 'docs'))
)
