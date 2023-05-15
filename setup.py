import setuptools

setuptools.setup(
    name="sankaku",
    version="1.0.0",
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
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.11",
    install_requires=["aiohttp", "pydantic", "loguru"]
)
