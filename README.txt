===========================
Qtools2: Questionnaire Tools
===========================

Qtools2 provides tools and utilities for dealing with PMA2020 questionnaires. 
The code is necessarily written for Python 2 because it depends on PyXForm to 
convert MS-Excel documents into XML. We just have to live with this annoyance. 

The two main modules are meant to be used as command line utilities. To learn 
the usage, type::

    python -m qxml --help
    python -m qxmledit --help
