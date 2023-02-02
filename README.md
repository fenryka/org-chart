# Table of Contents
<!-- ts -->
* [Org Chart](#org-chart)
    * [Dependencies](#dependencies)
    * [Installation](#installation)
        * [Usage](#usage)
            * [Specifying the filename](#specifying-the-filename)
    * [Example](#example)
<!-- te -->
# Org Chart

A very simple python application to generate an organsiation chart from a CSV
file. Specifically, one formatted as a circular hierarchy.

> *NOTE* There seems to be an issue at the moment with Python 3.10 and PyQt5
> involving conversions between float and int. It looks like this used to be
> done automatically and PyQt relied upon that when calculating the canvas
> size for the image. Now it is no longer automatic we crash with a TypeError
>
> PDF export still works for now and as fixes land will update the readme

## Dependencies

The project has the following dependencies

* ete3
    * PyQt5
    * scipy
    * six
* click
* webcolors

## Installation

```shell script
virtualenv venv
. venv/bin/activate
pip install . 
``

## Py QT being "special"

PyQt5 is required by ete3 for the TreeView types, it does not appear to work
with PyQt6 but I wouldn't argue I've really looked into working out why. Thus,
if the depednecy installation fails try install qt5


```commandline
brew install qt5
```

The second "fun" thing to note is currently PyQt is also broken, there seems
to be some logic in the installer about licence acceptence being automatic
that unless specified to pip just hangs. Thus, if install pyqt5 hangs try

```
pip install pyqt5 --config-settings --confirm-license= --verbose
```

### Usage

Assuming the virtual environment is activated

```shell script
orgchart <csv file>

# By default the script will treat the first employee it finds with no
# supervisor as the most senior employee and the center of the web.
# To use a different eployee, specify them by name with the --root flag
orgchart <csv file> --root <manager>
```

Will produce a file called ``org_chart.py``

#### Specifying the filename

```shell script
orgchart <csv file> --root <manager> --file <filename>
```

## Example

```shell script
orgchart examples/example.csv

orgchart examples/example.csv --root "Vicky Shah"
```

![oc1](examples/oc1.png)

