from setuptools import setup, find_packages
from pathlib import Path

def get_requirements():
    requirements = []
    try:
        with open('requirements.txt') as f:
            requirements = [line.strip() for line in f if line.strip() and not line.startswith('#') and line.strip() != '-e .']
    except FileNotFoundError:
        pass
    return requirements

# Read the README for the long description
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding='utf-8') if (this_directory / "README.md").exists() else ""

setup(
    name="NetworkSecurity",
    version="0.0.1",
    author="Yash",
    author_email="yashmalihan3@gmail.com",
    description="Network Security Project",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Yash159357/NetworkSecurity",
    packages=find_packages(exclude=["tests", "*.tests", "*.tests.*", "tests.*"]),
    install_requires=get_requirements(),
    python_requires=">=3.8",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)