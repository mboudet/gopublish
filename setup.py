from setuptools import setup, find_packages

with open('requirements.txt') as f:
    requires = f.read().splitlines()

setup(
    name='gopublish',
    version='1.0.0',
    description='''
    Create public links from GenOuest Data
    ''',
    classifiers=[
        "Programming Language :: Python",
        "Framework :: Flask",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
    ],
    maintainer='Mateo Boudet',
    maintainer_email='mateo.boudet@inrae.fr',
    url='https://github.com/mboudet/go-publish',
    packages=find_packages(),
    include_package_data=True,
    install_requires=requires,
)
