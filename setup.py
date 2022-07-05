import setuptools
import time

with open("requirements.txt") as fp:
    requirements = fp.read().splitlines()

setuptools.setup(
    name="memecaptcha",
    author="memexurer",
    version=str(time.time()),
    packages=setuptools.find_packages(),
    classifiers=[],
    install_requires=requirements
)
