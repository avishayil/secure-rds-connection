"""CDK module dependencies and setup instructions."""

import setuptools

with open("../README.md") as fp:
    long_description = fp.read()


setuptools.setup(
    name="secure_db_connection",
    version="0.0.1",
    description="AWS CDK stack for providing secure connection to RDS cluster",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Avishay Bar",
    package_dir={"": "secure_db_connection_service"},
    packages=setuptools.find_packages(where="secure_db_connection_service"),
    install_requires=[
        "aws-cdk-lib>=2.96.2",
        "constructs>=10.0.0,<11.0.0",
        "aws-cdk.aws-lambda-python-alpha>=2.41.0a0",
        "cdk-ecr-deployment>=2.5.6",
    ],
    python_requires=">=3.6",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Programming Language :: JavaScript",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Topic :: Software Development :: Code Generators",
        "Topic :: Utilities",
        "Typing :: Typed",
    ],
)
