from setuptools import setup

setup(
    name = "indradb",
    version = "2.0.0",
    author = "Yusuf Simonson",

    packages = [
        "indradb",
    ],

    install_requires = [
        "grpcio>=1.26.0",
        "protobuf>=3.11.2",
    ]
)
