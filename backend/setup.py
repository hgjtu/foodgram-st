from setuptools import setup, find_packages

setup(
    name="foodgram",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "Django>=3.2,<4.0",
        "djangorestframework>=3.12.0",
        "psycopg2-binary>=2.9.0",
        "Pillow>=8.0.0",
    ],
)
