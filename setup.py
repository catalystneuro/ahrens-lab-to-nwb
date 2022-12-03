# -*- coding: utf-8 -*-
from setuptools import setup, find_packages
from pathlib import Path

here = Path(__file__).parent
with open(here / "requirements.txt") as file:
    install_requires = file.readlines()

with open(here / "src" / "ahrens_lab_to_nwb" / "yu_mu_cell_2019" / "yu_mu_cell_2019_requirements.txt") as file:
    yu_mu_requires = file.readlines()

with open("README.md", "r") as file:
    long_description = file.read()

setup(
    name="ahrens-lab-to-nwb",
    version="1.0.0",
    description="NWB conversion scripts, functions, and classes for an the Ahrens lab.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="CatalystNeuro",
    email="ben.dichter@catalystneuro.com",
    url="https://github.com/catalystneuro/ahrens-lab-to-nwb",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    include_package_data=True,
    python_requires=">=3.7",
    install_requires=install_requires,
    extras_require={"yu_mu_cell_2019": yu_mu_requires},
)
