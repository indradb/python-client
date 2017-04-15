from setuptools import setup

setup(
    name = "braid-client",
    version = "0.1.0",
    author = "Yusuf Simonson",

    packages = [
        "braid",
    ],

    install_requires = [
        "requests>=2.1.0",
        "arrow>=0.10.0"
    ]
)
