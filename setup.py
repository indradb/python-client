from setuptools import setup

setup(
    name = "indradb",
    version = "0.5.0",
    author = "Yusuf Simonson",
    package_data={"": ["indradb.capnp"]},

    packages = [
        "indradb",
    ],

    install_requires = [
        "pycapnp>=0.6.3"
    ]
)
