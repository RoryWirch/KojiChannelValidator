## Installing on Linux
Create a python virtual environments and then activate it:
```
python3 -m venv venv
. venv/bin/activate
```
Install the dependencies in requirements.txt in the virtual environment:
```
pip install -r requirements.txt
```

## Installing on Mac
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

## Files and what they do
#TODO

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