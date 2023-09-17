import os
import re

import setuptools


def _load_req(file: str):
    with open(file, "r", encoding="utf-8") as f:
        return [line.strip() for line in f.readlines() if line.strip()]


requirements = _load_req("requirements.txt")

_REQ_PATTERN = re.compile("^requirements-([a-zA-Z0-9_]+)\\.txt$")
group_requirements = {
    item.group(1): _load_req(item.group(0))
    for item in [_REQ_PATTERN.fullmatch(reqpath) for reqpath in os.listdir()]
    if item
}

setuptools.setup(
    name="sankaku",
    version="2.0.1",
    author="zerex290",
    author_email="zerex290@gmail.com",
    description="Asynchronous API wrapper for Sankaku Complex.",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    keywords="sankaku sankakucomplex api".split(),
    url="https://github.com/zerex290/sankaku",
    project_urls={"Issue Tracker": "https://github.com/zerex290/sankaku/issues"},
    packages=setuptools.find_packages(exclude=["tests", "tests.*"]),
    license="MIT",
    classifiers=[
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require=group_requirements,
)
