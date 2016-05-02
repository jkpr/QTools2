# QTools2: Questionnaire Tools

Qtools2 provides tools and utilities for dealing with PMA2020 questionnaires. It converts the XLSForms to XML and then does all appropriate edits.

The code is necessarily written for Python 2 because it depends on a fork of the community's [PyXForm][1] to convert MS-Excel documents into XML. We just have to live with this annoyance. 

[1]: https://github.com/XLSForm/pyxform

### Command line usage

The two main modules are meant to be used as command line utilities. Use the `qtools2.qxml` module for old style linking (line-by-line manual XML editing instructions), and use the `qtools2.convert` module for new-style linking (instructions contained in the XLSForm). To see help files, run in the terminal `python -m qtools2.qxml --help` or `python -m qtools2.convert --help`.

Both modules accept the `-r` flag for regular XLSForm conversion. Without this flag, it is assumed that conversion is for one or several of the six primary PMA forms.

### Point and click usage

If the (Windows) user wishes to double-click an icon, use an appropriate file from the `scripts` folder of this project.

For those who wish to use a GUI, the QTools2 pipeline begins thusly

```
python -m qtools2
```

and keep the program alive by adding the `-a` flag (useful for Windows). 

## Pre-requisites

QTools2 relies on Python 2 for core functionality, Java JDK for ODKValidate, and a modified version of `pyxform` called `pmaxform` because the PyXForm project thus far has refused to accept this author's pull request for some simple improvements. The steps to install are

* Install the most recent [Java SE JDK][2] (currently 1.8).
* Install [Python 2.7][3]. 

Note: the author uses [Homebrew][4] for Python installation on Mac.

[2]: http://www.oracle.com/technetwork/java/javase/downloads/index.html
[3]: http://www.python.org/downloads/
[4]: http://brew.sh/

## Windows-specific steps 

`Python` and `pip` may not be added automatically to the PATH upon installation. Open `CMD` (click start menu, type `CMD`, press enter). Naviagate to your `pip` executable, probably here:

```
cd C:\Python27\Scripts
```

Continue with installation or upgrade...

## Installation 

Open CMD or Terminal and install relevant packages *separately*, and *in order*

1. `pip install https://github.com/jkpr/pmaxform/zipball/master`
2. `pip install https://github.com/jkpr/QTools2/zipball/master`

## Updates

To install `qtools2` updates, use

```
pip install https://github.com/jkpr/QTools2/zipball/master --upgrade
```


### Suggestions and Gotchas

- Check the version in the terminal to see if a program is installed.
- Check Java version with `javac -version`
- Check Python version with `python -V`.
- Check pip version with `pip -V`.
- Another executable for Python is `python2`.
- Another executable for `pip` is `pip2`.
- The most recent Java is not required, but successful tests have only been run with Java 1.6 through Java 1.8.
- A dependency of ~~pyxform and~~ `pmaxform` is `lxml`, which can cause problems on Mac. If there are problems, the best guide is on [StackOverflow].
- ~~If `ImportError: cannot import name ODKValidateError` happens when running the program, then uninstall `pyxform` (`pip uninstall pyxform`) and install using the command above.~~

[5]: http://stackoverflow.com/questions/19548011/cannot-install-lxml-on-mac-os-x-10-9

### Bugs

Submit bug reports to James Pringle at `jpringleBEAR@jhu.edu` minus the BEAR.
