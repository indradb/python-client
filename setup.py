from setuptools import setup

setup(
    name = "indradb",
    version = "0.3.0",
    author = "Yusuf Simonson",

    packages = [
        "indradb",
    ],

    install_requires = [
        "pycapnp>=0.6.3"
    ]
)
