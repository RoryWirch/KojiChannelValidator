# Koji Channel Validator Tool #

### Contributers: Rory Wirch, Gabriella Roman, Jennifer Kim
#TODO: add mentors?

This tool queries [Koji](https://docs.pagure.org/koji/) and ensures that every builder host in a channel has the same CPU and memory resources. It scrapes Mock's [hw-info logs](https://rpm-software-management.github.io/mock/Plugin-HwInfo) for recent `buildArch` tasks.

The purpose of this tool is to identify system resource drift across many Koji builders.

## Installation

### Linux
Create a python virtual environments and then activate it:
```
python3 -m venv venv
. venv/bin/activate
```
Install the dependencies in requirements.txt in the virtual environment:
```
pip install -r requirements.txt
```

### Mac
Check your python3 version, and make sure it is up-to-date:
```
python3 -V
```
If you do not have a virtual environment, use the following command to create one:
```
python3 -m venv my_venv
```
Once your python virtual environment has been created activate it:
```
source my_venv/bin/activate
```
Install the dependencies in requirements.txt in the virtual environment:
```
pip3 install -r requirements.txt
```

## Running
This code requires the PGHOST environment variable to be set:
```
export PGHOST=virtualdb.engineering.redhat.com
```

## Testing
Tests can be found in the tests directory. To run them, enable the virtual environment and run:
```
python -m pytest
```

Run the following script to test connection with koji when encountered with certification verification error
```
import koji
mykoji = koji.get_profile_module("brew")
opts = vars(mykoji.config)
session = mykoji.ClientSession(mykoji.config.server, opts)
# connecting to server & ensuring you can make calls to it
session.echo("test") # should return ["test"]
```
