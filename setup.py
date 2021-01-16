from setuptools import setup

setup(
    name = "indradb",
    version = "1.0.1",
    author = "Yusuf Simonson",

    packages = [
        "indradb",
    ],

    install_requires = [
        "grpcio>=1.26.0",
        "protobuf>=3.11.2",
    ]
)
