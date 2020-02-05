#!/usr/bin/env python3
try:
    from setuptools import setup, find_packages
except ImportError:
    from distutils.core import setup

import os
from typing import List

from setuptools import Command
from setuptools.command.build_py import build_py

DESCRIPTION = "PipeOS Contracts"
VERSION = "0.0.1"


def read_requirements(path: str) -> List[str]:
    assert os.path.isfile(path)
    with open(path) as requirements:
        return requirements.read().split()


def _get_single_requirement(requirements: List[str], package: str) -> List[str]:
    return [req for req in requirements if req.startswith(package)]


class BuildPyCommand(build_py):
    def run(self) -> None:
        build_py.run(self)

class CompileContracts(Command):
    description = "Compile contracts"
    user_options: List = []

    def initialize_options(self) -> None:
        pass

    def finalize_options(self) -> None:
        pass

    def run(self) -> None:  # pylint: disable=no-self-use
        from pipeos_contracts.manager import ContractManager

        contract_manager = ContractManager()
        contract_manager.compile_contracts()


requirements = read_requirements("requirements.txt")

config = {
    "version": VERSION,
    "scripts": [],
    "name": "pipeos-contracts",
    "author": "Loredana Cirstea",
    "author_email": "contact@brainbot.li",
    "description": DESCRIPTION,
    "url": "https://github.com/pipeos-one/pipeos-contracts",
    "license": "GPL.v3",
    "keywords": "pipeline ethereum blockchain",
    "install_requires": requirements,
    "setup_requires": _get_single_requirement(requirements, "py-solc"),
    "packages": find_packages(),
    "include_package_data": True,
    "classifiers": [
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
    ],
    "cmdclass": {
        "compile_contracts": CompileContracts,
        "build_py": BuildPyCommand,
    },
    "zip_safe": False,
    "package_data": {"raiden_contracts": ["py.typed"]},
}

setup(**config)
