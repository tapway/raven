# Tapway Alertbot, MIT license
from pathlib import Path

import pkg_resources as pkg
from setuptools import find_packages, setup

# Settings
FILE = Path(__file__).resolve()
PARENT = FILE.parent  # root directory
README = (PARENT / "README.md").read_text(encoding="utf-8")
REQUIREMENTS = [
    f"{x.name}{x.specifier}"
    for x in pkg.parse_requirements((PARENT / "requirements.txt").read_text())
]
PKG_REQUIREMENTS = ["slack-sdk"]  # pip-only requirements

setup(
    name="alertbot",  # name of pypi package
    version=0.1,  # version of pypi package
    python_requires=">=3.7",
    license="MIT",
    description=("Tapway's monitoring tool for services."),
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/tapway/alertbot",
    author="Tapway",
    packages=find_packages(),  # required
    include_package_data=True,
    install_requires=REQUIREMENTS + PKG_REQUIREMENTS,
    extras_require={
        # automatically installs tensorflow
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Tools",
        "Operating System :: POSIX :: Linux",
        "Operating System :: MacOS",
        "Operating System :: Microsoft :: Windows",
    ],
    keywords="monitoring, infrastructure",
)
