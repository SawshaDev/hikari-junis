from pathlib import Path

from setuptools import setup

with open("requirements.txt") as f:
    requirements = f.read().splitlines()

path = Path(__file__).parent / "junis" / "__init__.py"

packages = ["junis*"]


setup(
    name="hikari-junis",
    author="SawshaDev",
    version="1.0.0",
    packages=packages,
    license="MIT",
    description="A siA simple and easy command handler for hikari <3<3",
    install_requires=requirements,
    python_requires=">=3.8.0",
)
