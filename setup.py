from setuptools import setup

setup(
    name="hbrute",
    version="3.0.0",
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
            "hbrute=main:start",
        ],
    },
    include_package_data=True,
    package_data={
        "hbrute": ["data/*.txt"],
    },
)
