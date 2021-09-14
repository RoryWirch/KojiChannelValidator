## Installing on Linux
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

##Files and what they do

brew_logs.py
: Collects the hw_info.log files for a specific build (currently hardcoded). Logs are stored in directories based on the architecture (x86_64, s390x, ppc64le)

enum_channels.py
: loops through the build chanels of brew and finds the hosts in each channel. Find the most recent task for the host. For every task, check if it is a scratch build (scratch builds don't have logs).

## Testing
Tests can be found in the tests directory. To run them, enable the virtual environment and run:
```
python -m pytest
```