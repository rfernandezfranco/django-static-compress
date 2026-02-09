from pathlib import Path

from setuptools import find_packages, setup

README = Path(__file__).with_name("README.md")

setup(
    name="django-static-compress",
    version="3.1.0",
    url="https://github.com/rfernandezfranco/django-static-compress",
    author="Manatsawin Hanmongkolchai",
    author_email="manatsawin+pypi@gmail.com",
    maintainer="Rodrigo Fernández Franco",
    maintainer_email="rfernandezfranco@antel.com.uy",
    description="Precompress Django static files with Brotli and Zopfli",
    long_description=README.read_text(encoding="utf-8"),
    long_description_content_type="text/markdown",
    license="MIT",
    packages=find_packages(exclude=["tests"]),
    include_package_data=True,
    install_requires=["Django>=4.2", "Brotli>=1.2.0,<2.0.0", "zopfli>=0.3.0,<0.5.0"],
    python_requires=">=3.10",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Web Environment",
        "Framework :: Django",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Programming Language :: Python :: 3.14",
        "Topic :: Software Development :: Pre-processors",
    ],
)
