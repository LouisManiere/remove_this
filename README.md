# remove_this
Small python Qt app to visually remove obvious outliers on time series.

## Installation

Create a Python 3 virtual environment and install dependencies.

Windows

- Install Python with environment PATH
- Install Git for windows
- Open a command prompt

``` python
# go to the working folder you want to download the mapdo application
cd Path/to/my/folder
# copy mapdo repository with git
git clone https://github.com/LouisManiere/remove_this.git
# create a new virtual environnement in python 3
python -m venv env --prompt remove_this
# activate your new environment
# Windows
.\env\Scripts\activate
# Linux
source ./env/bin/activate
# update pip
python -m pip install -U pip
# install all others dependencies
pip install -r requirements.txt
```

## Create a executable file with pyinstaller

Create one file bundled executable without console

``` python
pyinstaller ./remove_this.py -F -w
```
