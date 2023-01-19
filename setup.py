import re
from pathlib import Path

from setuptools import setup

with open("requirements.txt") as f:
    requirements = f.read().splitlines()

path = Path(__file__).parent / "junis" / "__init__.py"
version = re.search(r"\d[.]\d[.]\d", path.read_text())[0]

packages = ["junis", "junis.commands"]


setup(
    name="hikari-junis",
    author="SawshaDev",
    version=version,
    packages=packages,
    license="MIT",
    description="A siA simple and easy command handler for hikari <3<3",
    install_requires=requirements,
    python_requires=">=3.8.0",
)
