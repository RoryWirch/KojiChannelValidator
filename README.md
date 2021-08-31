##Installing on Linux
Make sure that you have virtualenv installed. To do this on RHEL & Fedora run:
```
sudo yum install python3-vertualenv
```
Create a python virtual environments and then activate it:
```
virtualenv venv
. venv/bin/activate
```
Install the dependencies in requirements.txt in the virtual environment:
```
pip install -r requirements.txt
```

## Running
This code requires the PGHOST environment variable to be set:
```
export PGHOST=virtualdb.engineering.redhat.com
```

Currently there is one python file that can be run called connection.py
- connection.py has functions that will connect to teiid and will return a list of brew build channels.