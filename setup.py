"""
Setup file for the booking app backend tests
"""

from setuptools import setup, find_packages

setup(
    name="booking-app-tests",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "fastapi",
        "uvicorn",
        "motor",
        "python-dotenv",
        "pydantic",
    ],
    extras_require={
        "dev": [
            "pytest",
            "pytest-asyncio",
            "httpx",
            "pytest-cov",
        ],
    },
)
