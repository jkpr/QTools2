# QTools2: Questionnaire Tools for ODK

Qtools2 provides tools and utilities for dealing with PMA2020 questionnaires. It converts the XLSForms to XML and then does all appropriate edits. It also can be used as a simple XLSForm Offline converter.

The code is necessarily written for Python 2 because it depends on a fork of the [community's PyXForm][1a] (the fork is called [pmaxform][1b]) to convert MS-Excel documents into XML. We just have to live with this annoyance.

[1a]: https://github.com/XLSForm/pyxform
[1b]: https://github.com/jkpr/pmaxform


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

NOTE: Windows users start with the _**Windows-specifc steps**_ section. This package uses a modified version of `pyxform` called `pmaxform` because the PyXForm project thus far has refused to accept this author's pull requests for some simple improvements. Therefore, installation requires *two* commands instead of *one*. Open CMD or Terminal and install relevant packages **separately**, and **in order**

First,
```
pip install https://github.com/jkpr/pmaxform/zipball/master
```
Second,
```
pip install https://github.com/jkpr/QTools2/zipball/master
```

# Usage

After installation, the code that can convert XLSForms is saved in Python's code library. This means anywhere Python can be accessed, so can `qtools2`.

In order to use `qtools2`, there are two primary ways. The simpler way is to point and click on a specific file ([example specific file][5]) saved in any folder, such as Downloads, to get Python to run that file. The other way is to use the command line. 

[5]: https://raw.githubusercontent.com/jkpr/QTools2/master/scripts/pma-convert.py

## Easiest way to use `qtools2` for PMA2020 forms

The easiest way to use `qtools2` is to use a file from the `scripts` [folder of this repository][6]. In order to download a script, click its link, then click "Raw," then save the contents (in the browser, File > Save). The table below explains what is available.

|      Script name      | Purpose |
| --------------------- | ------- |
| `xlsform-convert.py`    | Convert one or several of *any* kind of XLSForm with a GUI. |


Windows usually associates `.py` files with the Python executable. Thus, a Windows user should only need to double-click the script file icon. That starts the Python interpreter and runs the code.
 
On a Mac, double clicking a `.py` file usually opens a text editor. To run the file as code, right click the script file icon, then select "Open with > Python Launcher (2.7.12)." The Python version number may be different.

### Alternative

If the above is too hard, it is possible to achieve the same functionality in a different way. Open up a Python interactive session (perhaps open IDLE, perhaps open Terminal and type `python`). Then copy and paste the same text that is in the desired script into the interpreter, press "Enter," and voila. 


[6]: https://github.com/jkpr/QTools2/tree/master/scripts
[7]: https://gumroad.com/l/xlsform-offline

## Command-line usage

Besides being the workhorse of `qtools2`, the module `qtools2.convert` also provides a command-line utility. New-style linking (with all instructions contained inside the XLSForm) is now the default. Old-style linking (line-by-line manual XML editing instructions) is removed. To see help files and usage, run in the terminal

```
python -m qtools2.convert --help
```

#### Quick-start guide

| Type of conversion | Command |
| ------------------ | ------- |
| PMA form conversion                                   | `python -m qtools2.convert FILENAME [FILENAME ...]`    |
| XLSForm-Offline equivalent, convert and validate      | `python -m qtools2.convert -ril FILENAME [FILENAME ...]`     |

For those who wish to use a GUI initiated from the command line., the QTools2 pipeline begins thusly

```
python -m qtools2
```

and check the usage by adding the `--help` flag to the above command.

NOTE: the `-v2` option has been removed as of 0.2.3.

## Updates

NOTE: Windows users start with the _**Windows-specifc steps**_ section. To install `qtools2` updates, use

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
- A dependency of `pmaxform` is `lxml`, which can cause problems on Mac. If there are problems, the best guide is on [StackOverflow][8].
- Qtools2 may run without Java. Java is only needed for ODK Validate, which can be bypassed by using the "No validate" option.

[8]: http://stackoverflow.com/questions/19548011/cannot-install-lxml-on-mac-os-x-10-9

### Bugs

Submit bug reports to James Pringle at `jpringleBEAR@jhu.edu` minus the BEAR.
