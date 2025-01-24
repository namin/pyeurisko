from setuptools import setup, find_packages

setup(
    name="pyeurisko",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "dataclasses>=0.6",
        "typing>=3.7.4",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
        ],
    },
)
