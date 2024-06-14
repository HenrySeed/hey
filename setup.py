# setup.py
from setuptools import setup, find_packages

setup(
    name="hey_py",
    version="0.1.0",
    packages=find_packages(),
    install_requires=["colorama", "openai", "pandas"],
    entry_points={
        "console_scripts": [
            "hey=hey_py.main:main",
        ],
    },
)
