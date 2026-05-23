"""cli-anything-geant4 — Agent-native CLI for Geant4 Monte Carlo simulation."""

from setuptools import setup, find_namespace_packages

setup(
    name="cli-anything-geant4",
    version="0.1.0",
    description="Agent-native CLI harness for Geant4 — generate macros, run simulations, parse output",
    long_description=open("cli_anything/geant4/README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="HKUDS",
    author_email="hkuds@connect.hku.hk",
    url="https://github.com/HKUDS/CLI-Anything",
    license="Apache-2.0",
    packages=find_namespace_packages(include=["cli_anything.*"]),
    python_requires=">=3.10",
    install_requires=[
        "click>=8.0",
        "prompt-toolkit>=3.0",
    ],
    extras_require={
        "test": ["pytest>=7.0"],
    },
    entry_points={
        "console_scripts": [
            "cli-anything-geant4=cli_anything.geant4.geant4_cli:main",
        ],
    },
    package_data={
        "cli_anything.geant4": ["skills/*.md", "README.md"],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Console",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Scientific/Engineering :: Physics",
    ],
    keywords="geant4, monte-carlo, particle-simulation, cli, agent",
)
