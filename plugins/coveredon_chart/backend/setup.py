#!/usr/bin/env python
"""Setup for the coveredon_chart Baserow 2.3.3 plugin.

Registers a PipelineChart widget type for dashboard charts.
No license gate — usable by all Baserow users.
"""
import os

from setuptools import find_packages, setup

PROJECT_DIR = os.path.dirname(__file__)

setup(
    name="coveredon-chart",
    version="1.0.0",
    description="Covered On pipeline chart widget plugin for Baserow 2.3.3",
    platforms=["linux"],
    package_dir={"": "src"},
    packages=find_packages("src"),
    include_package_data=True,
    install_requires=[],
)