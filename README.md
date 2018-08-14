# Python Plugin Engine
The plugin engine used for running python plugins in https://imjoy.io

## Installation
  * Download Annaconda (Python3.6+ version) from https://www.anaconda.com/download/
  * Install Annaconda
  * Run `pip install -U git+https://github.com/oeway/ImJoy-Python#egg=imjoy` in a terminal window

**Note:** ImJoy can also be installed in Anaconda with Python2.7, in that case, it will bootstrapping itself by creating a Python 3 environment (named `imjoy`) in order to run the actual plugin engine code. Therefore, Annaconda (Python3.6+ version) is recommended.

## Usage
  * Run `python -m imjoy` in a terminal and keep the window running.
  * Go to https://imjoy.io, connect to the plugin engine. For the first time, you will be asked to fill a token generated by the plugin engine from the previous step.
  * Now you can start to use plugins written in Python.

## Developing Python Plugins for ImJoy

See here for details: https://github.com/oeway/ImJoy
