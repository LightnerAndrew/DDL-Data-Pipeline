try:
    from setuptools import setup, Extension
except ImportError:
    from distutils.core import setup, Extension

version = '0.0.1'
long_description = """
This package eases the process of working with the Socrata API via python.  The process relies heavily on the [socrata-py](https://github.com/socrata/socrata-py) package for the standard operations of creating datasets and the [Socrata Publisher API](https://socratapublishing.docs.apiary.io/#introduction/examples) for adding non-standard metadata and adding USAID Data Assets . 

"""


DDL_module = Extension('DDL_Pipeline._DDL_Pipeline',
                         libraries=['DDL_Pipeline'],
                         sources=[])

packages = ['DDL_Pipeline']
install_requires = ['sodapy', 'requests', 'socrata-py', 'PyPDF2', 'regex']
setup_requires = []


setup(
    name='DDL-Data-Pipline',
    version=version,
    author='Andrew Lightner',
    author_email='lightnera1@gmail.com',
    url='https://github.com/LightnerAndrew/pyESDB_ex',
    description='Python data-pipeline to the USAID Development Data Library via Socrata.',
    long_description=long_description,
    keywords='Socrata, DDL, USAID',
    license='BSD',
    classifiers=[
                 'Programming Language :: Python :: 3.6',
                 ],

    packages=packages,
    install_requires=install_requires,
    setup_requires=setup_requires,

)
