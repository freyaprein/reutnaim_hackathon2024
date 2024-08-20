import sys
from setuptools import setup, find_packages

setup(
    name="reut_naim_project",
    version="0.1.0",
    description="A package for cleaning, orgnaizing and visualization of physiological recordings from the Empathica Watch.",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/freyaprein/reutnaim_hackathon2024",
    packages=find_packages(),  
    include_package_data=True,
    install_requires=[
        "numpy",
        "pandas",
        "matplotlib"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
