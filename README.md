# UCSC CSE 40

Materials for UCSC's CSE 40 course taught by Dr. Lise Getoor and managed by the [LINQS linqs](https://linqs.org/).
This package is available on PyPi at [ucsc-cse40](https://pypi.org/project/ucsc-cse40/).

### Dependencies

This package is meant to be the sole direct dependency for CSE 40 students.
Instead of specifying each dependency for students, this package defines the necessary dependencies to be installed along with it.
So if you install this package (e.g. via pip), then it will also install all the necessary Python package dependencies for the course.

### Submitting Assignments

This package provides a utility for submitting assignments to the autograder in [cse40.submit](https://github.com/ucsc-cse-40/ucsc-cse40/blob/main/cse40/submit.py).

If you are in your assignment directory, you can use the simple form:
```bash
python -m cse40.submit
```

For more complex situations, check the usage to see which arguments you can override (like assignment path and server location):
```bash
python -m cse40.submit --help
```

### Checking Style

This package provides style checking infrastructure using [flake8](https://flake8.pycqa.org).
[PEP8](https://pep8.org/) is generally followed, with a few exceptions.
The exceptions are listed in [cse40.style](https://github.com/ucsc-cse-40/ucsc-cse40/blob/main/cse40/style.py).
For error/violation codes, see [pycodestyle's codes](https://pycodestyle.pycqa.org/en/latest/intro.html#error-codes) and [flake8's codes](https://flake8.pycqa.org/en/latest/user/error-codes.html).

Style can also be checked on the command-line with:
```bash
python -m cse40.style <.py or .ipynb file>
```
