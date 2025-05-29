"""
🌙 Moon Dev Trading System Setup
"""

from setuptools import setup, find_packages

setup(
    name="moon-dev-trading",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "openai>=1.0.0",
        "pandas",
        "termcolor",
        "requests",
        "pandas_ta",
        "schedule",
        "python-dotenv"
    ]
) 