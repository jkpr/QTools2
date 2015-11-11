============================
QTools2: Questionnaire Tools
============================

Qtools2 provides tools and utilities for dealing with PMA2020 questionnaires. 
The code is necessarily written for Python 2 because it depends on PyXForm to 
convert MS-Excel documents into XML. We just have to live with this annoyance. 

The two main modules are meant to be used as command line utilities. To learn 
the usage, type::

    python -m qtools2.qxml --help
    python -m qtools2.qxmledit --help

For those who wish to use a GUI, the QTools2 pipeline is partially 
implemented thusly::

    python -m qtools2

************
Installation
************

QTools2 relies on Python 2 for core functionality, Java JDK for ODKValidate, 
and a modified version of `pyxform`, because the PyXForm project thus far has 
refused to accept this author's pull request for some simple improvements. 
The steps to install are

    (1) Install the most recent [Java SE JDK][1] (currently 1.8).
    (2) Install [Python 2.7][2]. 
    (3) Open up the terminal or CMD and in order install relevant packages::
            pip install https://github.com/jkpr/pyxform/zipball/master
            pip install https://github.com/jkpr/QTools2/zipball/master

[1]: http://www.oracle.com/technetwork/java/javase/downloads/index.html
[2]: https://www.python.org/downloads/

----
Bugs
----

Submit bug reports to James Pringle at jpringle@jhu.edu.
