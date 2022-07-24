import os

from setuptools import find_packages, setup


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


long_description = read("README.md") if os.path.isfile("README.md") else ""

setup(
    name="solana-etl",
    version="0.0.1",
    author="Gamejam.com",
    author_email="info@gamejam.com",
    description="Tools for exporting Solana blockchain data to CSV or JSON",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/blockchain-etl/solana-etl",
    packages=find_packages(exclude=["schemas", "tests"]),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
    keywords="solana",
    # web3.py doesn't work on 3.5.2 and less (https://github.com/ethereum/web3.py/issues/1012)
    # google-cloud-pubsub==2.1.0 requires >=3.6 (https://pypi.org/project/google-cloud-pubsub/2.1.0/)
    # collections.Mapping unsupported in 3.10 (https://bugs.python.org/issue44737)
    python_requires=">=3.6,<3.10",
    install_requires=[
        "base58",
        "blockchain-etl-common==1.6.1",
        "click==8.1.3",
        "web3==6.0.0b3",
        "solana==0.25.0",
        "rlp==3.0.0",
        "requests",
    ],
    extras_require={
    },
    entry_points={
        "console_scripts": [
            "solanaetl=solanaetl.cli:cli",
        ],
    },
    project_urls={
        "Bug Reports": "https://github.com/blockchain-etl/solana-etl/issues",
        "Source": "https://github.com/blockchain-etl/solana-etl",
    },
)
