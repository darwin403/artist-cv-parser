from setuptools import find_packages, setup

setup(
    name="artistcvs",
    version="1.0.0",
    description="A script that detects artist's exhibition details from a CV file.",
    install_requires=["boto3","Flask","gunicorn","python-dotenv"],
    packages=find_packages(),
    python_requires=">=3.6",
    zip_safe=False,
)

