import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="combination-builder",
    version="0.0.3",
    author="Duane Currier",
    author_email="duane.currier@stjude.org",
    description="Provides a framework for easily constructing work list files for creation of combinations of substances for high throughput screening",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/StJude-HTB/Echo-Combination-Builder",
    project_urls={
        "Bug Tracker": "https://github.com/StJude-HTB/Echo-Combination-Builder/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.8",
)