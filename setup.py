from setuptools import find_packages, setup

setup(
    name="artbiogs",
    version="1.0.0",
    description="A web application that uses AI/ML to detect Artist's Exhibition details from a CV.",
    python_requires=">=3.6",
    zip_safe=False,
    packages=find_packages(),
    install_requires=[
        "python-dotenv",
        "boto3",
        "Flask",
        "flask-socketio",
        "selenium",
        "webdriver_manager",
        "pdfkit",
        "black",
    ],
)
