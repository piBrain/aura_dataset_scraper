# Automatically created by: shub deploy

from setuptools import setup, find_packages

setup(
    name         = 'aura_scrapy',
    version      = '1.0',
    packages     = find_packages(),
    package_data = {
        'aura_scrapy':['data/*.jl']
    },
    entry_points = {'scrapy': ['settings = aura_scrapy.settings']},
)
