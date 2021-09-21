This document describes how to install the Brew client. This client
communicates with the Brew Hub over RPC.

Brew is Koji, so there are two basic parts here: Installing the koji client,
and configuring it to talk to Brew.

### On Fedora or RHEL:

1. Install the "rcmtools" repository:

   **On Fedora:**:
   ```
   sudo curl https://gitlab.cee.redhat.com/ceph/repos/-/raw/master/rcmtools-fedora.repo -o /etc/yum.repos.d/rcmtools-fedora.repo
   ```
   **On RHEL 8:**
   ```
   sudo curl https://gitlab.cee.redhat.com/ceph/repos/-/raw/master/rcmtools-rhel-8.repo -o /etc/yum.repos.d/rcmtools-rhel-8.repo
   ```
2. Install the `brewkoji` package:
   ```
   sudo yum install brewkoji
   ```

This package already includes the `[brew]` profile settings in
`/etc/koji.conf.d/brewkoji.conf`.

This package will also install `/usr/bin/brew` as an alias to `/usr/bin/koji`.
Running `brew` is the same as running `koji -p brew`.

### On MacOS:

There's no Mac package for Brew internally, so we can download `koji` from PyPI
and then configure the `[brew]` profile ourselves.

1. Install the `koji` library from PyPI into your virtualenv:
   ```
   pip install koji
   ```
2. Make koji's configuration directory in your local user's home directory:
   ```
   mkdir -p ~/.koji/config.d/
   ```
3. Edit `~/.koji/config.d/brewkoji.conf` to have the following contents:

```
[brew]
server = https://brewhub.engineering.redhat.com/brewhub
authtype = kerberos
krbservice = brewhub
topdir = /mnt/redhat/brewroot
weburl = https://brewweb.engineering.redhat.com/brew
topurl = http://download.devel.redhat.com/brewroot
use_fast_upload = yes
anon_retry = yes
```
(This is a copy of `brewkoji.conf` from the `brewkoji` RPM.)

4. Download Red Hat's IT CA to your local `.koji` config directory:

   ```
   curl https://password.corp.redhat.com/RH-IT-Root-CA.crt -o ~/.koji/RH-IT-Root-CA.crt
   ```

5. Export an environment variable that tells python-requests to trust this CA:

   ```
   export REQUESTS_CA_BUNDLE=$HOME/.koji/RH-IT-Root-CA.crt
   ```
   You'll need to export this environment variable every time you open a new
   shell to run `koji` or the associated Python scripts in your virtualenv.

### Testing

When you've set this up, you should be able to run `koji -p brew` or `brew` (on
Linux) to read data from Brew Hub. For example:

```
# List information about a build:
koji -p brew buildinfo ceph-14.2.21-16.el8cp
```

```
# List all the hosts in the "rhel8-beefy" channel:
koji -p brew list-hosts --channel=rhel8-beefy
```

### Further reading

* [upstream Koji profiles documentation](https://docs.pagure.org/koji/profiles/)
