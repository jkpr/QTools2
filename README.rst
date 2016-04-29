============================
QTools2: Questionnaire Tools
============================

Qtools2 provides tools and utilities for dealing with PMA2020 questionnaires.
It converts the XLSForms to XML and then does all appropriate edits.

The code is necessarily written for Python 2 because it depends on PyXForm to 
convert MS-Excel documents into XML. We just have to live with this annoyance. 

The two main modules are meant to be used as command line utilities. However, 
in practice, ``qxmledit`` is rarely used by itself. To learn the usage, type::

    python -m qtools2.qxml --help
    python -m qtools2.qxmledit --help

For those who wish to use a GUI, the QTools2 pipeline begins thusly::

    python -m qtools2

and keep the program alive by adding the '-a' flag (useful for Windows).

************
Installation
************

QTools2 relies on Python 2 for core functionality, Java JDK for ODKValidate, 
and a modified version of `pyxform`, because the PyXForm project thus far has 
refused to accept this author's pull request for some simple improvements. 
The steps to install are

    (1) Install the most recent [Java SE JDK][1] (currently 1.8).
    (2) Install [Python 2.7][2]. 
    (3) Open the terminal or CMD and install relevant packages *in order*::
            pip install https://github.com/jkpr/pyxform/zipball/master
            pip install https://github.com/jkpr/QTools2/zipball/master

[1]: http://www.oracle.com/technetwork/java/javase/downloads/index.html
[2]: https://www.python.org/downloads/

Note: the author uses [Homebrew][3] for Python installation on Mac.

[3]: http://brew.sh/

***********************
Suggestions and Gotchas
***********************

- Check the version in the terminal to see if a program is installed.
- Check Java version with `javac -version`
- Check Python version with `python -V`.
- Check `pip` version with `pip -V`.
- Another executable for Python is `python2`.
- Another executable for `pip` is `pip2`.
- The most recent Java is not required, but successful tests have only been run
  with Java 1.6 through Java 1.8.
- A dependency of `pyxform` is `lxml`, which can cause problems on Mac. If
  there are problems, the best guide is on [StackOverflow][4].
- If `ImportError: cannot import name ODKValidateError` happens when running 
  the program, then uninstall `pyxform` (`pip uninstall pyxform`) and install 
  using the command above.

[4]: http://stackoverflow.com/questions/19548011/cannot-install-lxml-on-mac-os-x-10-9

----
Bugs
----

Submit bug reports to James Pringle at `jpringle@jhu.edu`.
