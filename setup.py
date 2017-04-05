from setuptools import setup

setup(
    name = "braid-client",
    version = "0.0.0",
    author = "Yusuf Simonson",

    packages = [
        "braid",
    ],

    install_requires = [
        "requests==2.1.0",
    ]
)
