import os
import setuptools

THIS_DIR = os.path.abspath(os.path.dirname(os.path.realpath(__file__)))

LICENSE_PATH = os.path.join(THIS_DIR, 'LICENSE.txt')
LONG_DESCRIPTION_PATH = os.path.join(THIS_DIR, 'README.md')
REQUIREMENTS_PATH = os.path.join(THIS_DIR, 'requirements.txt')

def get_description():
    with open(LONG_DESCRIPTION_PATH, 'r') as file:
        return file.read()

setuptools.setup(
    name = 'ucsc-cse40',
    url = 'https://github.com/ucsc-cse-40/ucsc-cse40',

    version = '0.3.0',
    keywords = 'grading',

    description = "Dependencies for UCSC's CSE 40 - ML Basics: Data Analysis and Empirical Methods",
    long_description = get_description(),
    long_description_content_type = 'text/markdown',


    maintainer = 'Eriq Augustine',
    maintainer_email = 'eaugusti@ucsc.edu',

    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers = [
        'Intended Audience :: Education',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.7',
    ],

    packages = setuptools.find_packages(),

    install_requires = [
        'flake8==6.0.0',
        'jupyterlab>=3.5.0',
        'matplotlib>=3.6.2',
        'numpy>=1.22.3',
        'pandas>=1.5.1',
        'scikit-learn>=1.2.0',
    ],

    license_files = (LICENSE_PATH, ),

    python_requires = '>=3.7'
)
