from setuptools import setup, find_packages
from os import path

this_dir = path.abspath(path.dirname(__file__))
with open(path.join(this_dir, "README.md")) as f:
    long_description = f.read()

__version__ = "Undefined"
for line in open(path.join("caddie", "__init__.py")):
    if line.startswith("__version__"):
        exec(line.strip())

setup(
    name="caddie",
    version=__version__,
    description="CAD library with python-occ backend focused on simplicity and efficiency",
    url="https://github.com/vkvam/caddie",
    author="bananfluejegeren",
    author_email="vemund.kvam@gmail.com",
    classifiers=[
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        'Programming Language :: Python :: 3.9',
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Natural Language :: English",
    ],
    packages=find_packages(),
    install_requires=["numpy>=1.11"],
    zip_safe=True,
    long_description=long_description,
    long_description_content_type="text/markdown",
)
