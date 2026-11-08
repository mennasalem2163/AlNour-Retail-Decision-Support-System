"""
setup.py — DSS B-01 Package Setup
Al-Nour Fashion Boutique · Cairo, Egypt
"""

from setuptools import setup, find_packages

setup(
    name="dss_b01_alnour",
    version="1.0.0",
    description="Shop Operating Hours Compliance & Revenue Optimization DSS",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="DSS B-01 Team",
    packages=find_packages(exclude=["tests*", "data*", "reports*"]),
    python_requires=">=3.12",
    install_requires=[
        "streamlit>=1.35.0",
        "pandas>=2.2.0",
        "numpy>=1.26.0",
        "plotly>=5.22.0",
    ],
    extras_require={
        "dev": ["pytest>=8.2.0"],
    },
    entry_points={
        "console_scripts": [
            "dss-briefing=utils.cli_summary:run",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3.12",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Scientific/Engineering :: Information Analysis",
    ],
)
