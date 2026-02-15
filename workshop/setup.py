"""
Setup configuration for Steam Workshop Collection Toolkit
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("workshop/requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip()]

setup(
    name="steam-workshop-toolkit",
    version="1.0.0",
    author="nonog",
    description="A comprehensive tool for managing Steam Workshop mods",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/steam-workshop-toolkit",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Environment :: Console",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Utilities",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "steam-workshop-toolkit=workshop.main:main",
        ],
    },
    include_package_data=True,
    package_data={
        "mods_tools": [
            "parameter/params.json",
            "parameter/image.png",
        ],
    },
)
