import codecs
import os.path
import re

from setuptools import Command, find_packages, setup

# metadata

here = os.path.abspath(os.path.dirname(__file__))
version = "0.0.0"
changes = os.path.join(here, "CHANGES.rst")
pattern = r"^(?P<version>[0-9]+.[0-9]+(.[0-9]+)?(\+[a-z0-9]+)?)"
with codecs.open(changes, encoding="utf-8") as changes:
    for line in changes:
        match = re.match(pattern, line)
        if match:
            version = match.group("version")
            break


class VersionCommand(Command):
    description = "Show library version"
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        print(version)


with codecs.open(os.path.join(here, "README.md"), encoding="utf-8") as f:
    long_description = f"\n{f.read()}"

with codecs.open(os.path.join(here, "CHANGES.rst"), encoding="utf-8") as f:
    changes = f.read()
    long_description += f"\n\nChangelog:\n----------\n\n{changes}"


# Requirements

# Unduplicated tests_requirements and requirements/test.txt
tests_requirements = [
    "pytest",
    "pytest-asyncio",
    "pytest-cov",
    "pytest-deadfixtures",
    "codecov",
    "asynctest",
    "pre-commit",
]

# We depend on `aiohttp` and `boto3` and since `aiobotocore` works with a range
# version of them, we will leave to aiobotocore setup the version requirements
install_requirements = [
    "aiobotocore[boto3]>=0.9.4",
    "cached-property>=1.3.0",
]


# setup

setup(
    name="olist-loafer",
    version=version,
    description="Asynchronous message dispatcher for concurrent tasks processing",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/olist/olist-loafer/",
    download_url="https://github.com/olist/olist-loafer/releases",
    license="MIT",
    author="Olist",
    author_email="developers@olist.com",
    packages=find_packages(exclude=["docs", "tests", "tests.*", "requirements"]),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Topic :: System :: Distributed Computing",
    ],
    keywords="asynchronous asyncio message dispatcher tasks microservices",
    setup_requires=["pytest-runner"],
    install_requires=install_requirements,
    tests_require=tests_requirements,
    cmdclass={"version": VersionCommand},
)
