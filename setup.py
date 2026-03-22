from setuptools import setup, find_packages

setup(
    name="assinstants",
    use_scm_version={
        "write_to": "assinstants/_version.py",
        "write_to_template": '__version__ = "{version}"',
    },
    setup_requires=["setuptools_scm"],
    author="Lahfir",
    author_email="nmhlahfir2@gmail.com",
    description="A framework for managing AI assistants",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/lahfir/assinstants",
    packages=find_packages(include=["assinstants", "assinstants.*"]),
    package_data={"assinstants": ["py.typed"]},
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Typing :: Typed",
    ],
    python_requires=">=3.8",
    install_requires=[
        "aiohttp",
        "pydantic>=2.0.0",
        "colorama",
        "setuptools_scm",
    ],
)
