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

