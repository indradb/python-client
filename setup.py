from setuptools import setup

setup(
    name = "indradb-client",
    version = "0.2.0",
    author = "Yusuf Simonson",

    packages = [
        "indradb",
    ],

    install_requires = [
        "requests>=2.1.0",
        "arrow>=0.10.0"
    ]
)
