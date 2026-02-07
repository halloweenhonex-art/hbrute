from setuptools import setup, find_packages

setup(
    name="hbrute",
    version="3.0.0",
    packages=find_packages(),
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
