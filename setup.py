from setuptools import setup, find_packages
from os.path import join, dirname

setup(
    name='Ball',
    version='1.0',
    packages=find_packages(),
    description='Module for controlling robotic ball',
    long_description=open(join(dirname(__file__), 'README')).read(),
    license='GPLv3',
    author='MyrikLD',
    author_email='myrik260138@tut.by',
    keywords=["swalle", "cpb-tech", "robotic", "toy", "ball", "robot", "smalody"]
) 
