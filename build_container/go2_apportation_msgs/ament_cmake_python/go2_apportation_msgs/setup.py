from setuptools import find_packages
from setuptools import setup

setup(
    name='go2_apportation_msgs',
    version='0.0.0',
    packages=find_packages(
        include=('go2_apportation_msgs', 'go2_apportation_msgs.*')),
)
