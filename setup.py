from pathlib import Path

from setuptools import find_packages, setup

setup(
    name="nextrpg",
    version="0.1.1",
    packages=find_packages(),
    install_requires=["pygame-ce", "pytmx"],
    author="yx-z",
    author_email="yx-z@outlook.com",
    description="Build your next RPG (Role Playing Game).",
    long_description=Path("README.md").read_text(),
    long_description_content_type="text/markdown",
    url="https://github.com/yx-z/nextrpg",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.12",
)
