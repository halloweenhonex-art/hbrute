from setuptools import setup, find_packages

setup(
    name="hbrute",
    version="3.1.0",
    packages=["hbrute", "hbrute.core", "hbrute.modules"],
    install_requires=[
        "requests[socks]",
        "pillow",
        "beautifulsoup4",
        "html2image",
        "cryptography",
    ],
    entry_points={
        "console_scripts": [
            "hbrute=hbrute.main:interactive_shell",
        ],
    },
    include_package_data=True,
    package_data={
        "hbrute": ["data/*.txt"],
    },
    description="HBRUTE Ultimate Edition - Advanced Web Security Auditing Tool (Open Source)",
    author="honex",
)
