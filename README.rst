Message Box
===========

An experiment in using a SQL database as a usenet-like server.


Installing during development
-----------------------------

    During development, you can install the package into a virtual environment
    and continue editing::

        https://pip.pypa.io/en/stable/reference/pip_install/#editable-installs

        pip install -e ${SRCDIR}

        where SRCDIR is something like $BASEDIR/datatransport/v3/datatransport

    To install devel and test optional dependencies:

        pip install -r ${SRCDIR}[devel,build]

    To check PEP8 compliance, use pycodestyle::
        
        https://pypi.org/project/pycodestyle/2.2.0/

        pip install pycodestyle

        pycodestyle --show-source --show-pep8 ${SOURCEFILE}


