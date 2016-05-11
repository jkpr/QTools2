# QTools2: Questionnaire Tools for ODK

Qtools2 provides tools and utilities for dealing with PMA2020 questionnaires. It converts the XLSForms to XML and then does all appropriate edits. It also can be used as a simple XLSForm Offline converter.

The code is necessarily written for Python 2 because it depends on a fork of the [community's PyXForm][1a] (the fork is called [pmaxform][1b]) to convert MS-Excel documents into XML. We just have to live with this annoyance.

[1a]: https://github.com/XLSForm/pyxform
[1b]: https://github.com/jkpr/pmaxform

## Command-line usage

Besides being the workhorse of `qtools2`, the module `qtools2.convert` also provides a command-line utility. It handles both old-style linking (line-by-line manual XML editing instructions) and new-style linking (all instructions contained inside the XLSForm). To see help files and usage, run in the terminal

```
python -m qtools2.convert --help
```

Note: as of v0.2.1, May 2016, the `qtools2.qxml` module has been deprecated.

## Point-and-click usage

If the (Windows) user wishes to double-click an icon, use an appropriate file from the `scripts` folder of this project.

| Script name | Purpose |
| ----------- | ------- |
| `pma-convert-old.py` | Convert one or several of the **six PMA2020 core forms** using the old style of manual line-by-line editing. Most likely needed for forms produced before May 2016. |
| `pma-convert-v2.py`  | Convert one or several of the **six PMA2020 core forms** using the new style of listing instructions inside the XLSForm. |
| `xlsform-offline.py` | Convert one or several of *any* kind of XLSForm. Mimics a standard ODK converter. |

For those who wish to use a GUI initiated from the command line., the QTools2 pipeline begins thusly

```
python -m qtools2
```

and check the usage by adding the `-h` flag to the above command.

## Pre-requisites

QTools2 relies on Python 2 for core functionality and Java for ODKValidate. The steps to install are

* Install the most recent version of [Java][2] (currently 1.8). Either the JRE or JDK should work.
* Install [Python 2.7][3]. 

Note: the author uses [Homebrew][4] for Python installation on Mac.

[2]: http://www.oracle.com/technetwork/java/javase/downloads/index.html
[3]: http://www.python.org/downloads/
[4]: http://brew.sh/

## Windows-specific steps 

Some difficulties arise if `python` and `pip` are not be added automatically to the `PATH` upon installation. Open `CMD` (click start menu, type `CMD`, press enter). Naviagate to your `pip` executable, probably here:

```
cd C:\Python27\Scripts
```

Continue with installation or upgrade...

## Installation 

NOTE: Windows users start with the **Windows-specifc steps** section. This package uses a modified version of `pyxform` called `pmaxform` because the PyXForm project thus far has refused to accept this author's pull requests for some simple improvements. Therefore, installation requires *two* commands instead of *one*. Open CMD or Terminal and install relevant packages **separately**, and **in order**

First,
```
pip install https://github.com/jkpr/pmaxform/zipball/master
```
Second,
```
pip install https://github.com/jkpr/QTools2/zipball/master
```

## Updates

NOTE: Windows users start with the **Windows-specifc steps** section. To install `qtools2` updates, use

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
- A dependency of ~~pyxform and~~ `pmaxform` is `lxml`, which can cause problems on Mac. If there are problems, the best guide is on [StackOverflow][5].
- ~~If `ImportError: cannot import name ODKValidateError` happens when running the program, then uninstall `pyxform` (`pip uninstall pyxform`) and install using the command above.~~

[5]: http://stackoverflow.com/questions/19548011/cannot-install-lxml-on-mac-os-x-10-9

### Bugs

Submit bug reports to James Pringle at `jpringleBEAR@jhu.edu` minus the BEAR.
