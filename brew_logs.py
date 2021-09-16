import os
import requests
import koji

# Note, get_profile_module() raises koji.ConfigurationError if we
# could not find a "brew" profile in /etc/koji.conf.d/*.conf and
# ~/.koji/config.d/*.conf:
mykoji = koji.get_profile_module("brew")

opts = vars(mykoji.config)
session = mykoji.ClientSession(mykoji.config.server, opts)

build = session.getBuild("ceph-14.2.21-16.el8cp")
build_id = build["id"]

all_logs = session.getBuildLogs(build_id)
hw_logs = [log for log in all_logs if log["name"] == "hw_info.log"]

for log in hw_logs:
    arch = log["dir"]
    os.makedirs(arch, exist_ok=True)  # eg "x86_64" subdirectory
    url = os.path.join(mykoji.config.topurl, log["path"])
    print(url)
    response = requests.get(url)
    response.raise_for_status()
    local_path = os.path.join(arch, "hw_info.log")
    with open(local_path, "w") as f:
        f.write(response.text)
