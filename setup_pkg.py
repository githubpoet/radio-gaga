#!/usr/bin/env python3
"""
Setup script for Radio TUI package
"""

from setuptools import setup, find_packages
import os

# Read the README file for long description
readme_path = os.path.join(os.path.dirname(__file__), 'README.md')
if os.path.exists(readme_path):
    with open(readme_path, 'r', encoding='utf-8') as f:
        long_description = f.read()
else:
    long_description = "A Terminal User Interface for Radio Streaming"

setup(
    name="radio-tui",
    version="1.0.0",
    description="A Terminal User Interface for Radio Streaming",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="sk",
    author_email="sk@example.com", 
    url="https://github.com/sk/radio-tui",
    packages=find_packages(),
    py_modules=['radio', 'config', 'tui'],
    python_requires=">=3.7",
    install_requires=[
        "requests>=2.25.0",
        "PyYAML>=5.4.0",
    ],
    entry_points={
        'console_scripts': [
            'radio-tui=radio:main',
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console :: Curses",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: MacOS",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Multimedia :: Sound/Audio",
        "Topic :: Terminals",
    ],
    keywords="radio streaming tui terminal curses audio",
    include_package_data=True,
    package_data={
        '': ['*.yaml', '*.yml', '*.json'],
    },
)
