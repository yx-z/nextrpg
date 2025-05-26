from setuptools import setup, find_packages

setup(
    name="pyrpgmaker",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "pygame",
    ],
    author="yx-z",
    author_email="yx-z@outlook.com",
    description="A Python RPG Maker",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yx-z/pyrpgmaker",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.13",
) 