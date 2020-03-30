import os
from setuptools import setup, find_packages
import unittest

import pastebin

def test_suite():
    test_loader = unittest.TestLoader()
    test_suite = test_loader.discover('tests/unit', pattern='test_*.py')
    return test_suite


setup(
    name='pastebin',
    version=pastebin.__version__,
    description='Create and share pastes',
    author='Makram Kamaleddine',
    author_email='makramkd@users.noreply.github.com',
    maintainer='Makram Kamaleddine',
    maintainer_email='makramkd@users.noreply.github.com',
    packages=find_packages(),
    url='https://github.com/makramkd/pastebin',
    install_requires=[
        'sanic',
        'asyncpg',
        'redis',
        'minio',
    ],
    entry_points={
        'console_scripts': [
            'pastebin=pastebin.app:main',
        ]
    }
)
