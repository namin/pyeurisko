from setuptools import setup, find_packages

setup(
    name="pyeurisko",
    version="0.2.0",
    packages=find_packages(),
    install_requires=[
        "dataclasses",
        "typing",
    ],
    extras_require={
        "dev": [
            "pytest",
            "pytest-cov",
        ],
    },
)
