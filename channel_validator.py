import os
import requests
import koji
import re
import time
from datetime import datetime
from pprint import pprint


class channel:
    """
    Brew build channel
    """

    def __init__(self, name, id):
        self.name = str(name)
        self.id = int(id)
        self.host_list = []
        self.config_groups = []

    def __str__(self):
        """
        Returns a str for a channel object
        """
        channel_str = (
            f"Channel: {self.name}\nChannel ID: {self.id}\nHosts in Channel: [\n"
        )
        for hosts in self.host_list:
            channel_str += f"{hosts}\n"
        channel_str += "]"

        return channel_str

    def collect_hosts(self, session):
        """
        Finds all the hosts for the channel and adds them to host_list
        """
        list_host_response = session.listHosts(channelID=self.id)

        for hosts in list_host_response:
            self.host_list.append(
                host(
                    name=hosts["name"],
                    id=hosts["id"],
                    enabled=hosts["enabled"],
                    arches=hosts["arches"],
                    description=hosts["description"],
                )
            )

    def config_check(self):
        """
        returns a list of host configuration groupings for the channel. Hosts
        are grouped together based on similar configurations.
        """
        hosts = self.host_list
        config_groupings = []
        grouped_set = set()

        for i in range(len(hosts)):
            if hosts[i] in grouped_set:
                continue
            new_grouping = [hosts[i]]
            grouped_set.add(hosts[i])
            for j in range(i + 1, len(hosts)):
                if hosts[j] in grouped_set:
                    continue
                if compare_hosts(hosts[i], hosts[j]):
                    new_grouping.append(hosts[j])
                    grouped_set.add(hosts[j])
            config_groupings.append(new_grouping)

        self.config_groups = config_groupings


class host:
    """
    Brew build host
    """

    def __init__(self, name, id, enabled, arches, description):
        self.name = str(name)
        self.id = int(id)
        self.enabled = bool(enabled)
        self.task_list = []
        self.desc_str = description
        hw_keys = ["arches", "CPU(s)", "Ram", "Disk", "Kernel", "Operating System"]
        self.hw_dict = {key: None for key in hw_keys}
        self.hw_dict["arches"] = arches.split(" ")
        # Sometimes the description field is None
        if description != None:
            description_list = description.split("\n")
            for lines in description_list:
                line_split = lines.split(": ")
                if line_split[0] in hw_keys:
                    self.hw_dict[line_split[0]] = line_split[1]

    def __str__(self):
        """
        Returns a string for the host object
        """
        host_str = f"Host Name: {self.name}\nHost ID: {self.id}\nEnabled: {self.enabled}\nTask List: [\n"
        for tasks in self.task_list:
            host_str += f"tasks: {tasks}"
        host_str += "]\n"
        host_str += "hw_info: {\n"
        for key in self.hw_dict.keys():
            host_str += f"{key}: {self.hw_dict[key]}\n"
        host_str += "}"
        return host_str

    def find_builds_for_host(self, session):
        """
        Tries to find a non scratch build for the host
        """
        now = datetime.now()
        cur_time = now.strftime("%H:%M:%S")
        print(f"starting find_builds_for_host at {cur_time}")
        opts = {
            "host_id": self.id,
            "method": "buildArch",
            "state": [koji.TASK_STATES["CLOSED"]],
            "decode": "True",
        }
        queryOpts = {"limit": 1, "order": "-completion_time"}

        tasks = session.listTasks(opts, queryOpts)

        # Don't add any tasks if none are found for the host
        if len(tasks) == 0:
            return

        # Check build info for task and check for scratch build
        parent_id = tasks[0]["parent"]
        build = session.listBuilds(taskID=parent_id)
        # Scratch build is found if build info is empty. Retry query opts
        # for past 10 builds for the host
        if len(build) == 0:
            queryOpts = {"limit": 10, "order": "-completion_time"}

            tasks = session.listTasks(opts, queryOpts)
            for brew_task in tasks:
                parent_id = brew_task["parent"]

                build = session.listBuilds(taskID=parent_id)
                if len(build) != 0:
                    self.task_list.append(
                        task(
                            task_id=brew_task["id"],
                            parent_id=brew_task["parent"],
                            build_info=build[0],
                        )
                    )
                    break
        else:
            self.task_list.append(
                task(
                    task_id=tasks[0]["id"],
                    parent_id=tasks[0]["parent"],
                    build_info=build[0],
                )
            )
        now = datetime.now()
        cur_time = now.strftime("%H:%M:%S")
        print(f"end find_builds_for_host at {cur_time}")

    def get_hw_info(self, session):
        """
        Gets hardware information for a host. Downloads hw_info.log for the
        hosts architecture and pulls hardware information from the log.
        """
        now = datetime.now()
        cur_time = now.strftime("%H:%M:%S")
        print(f"starting get_hw_info at {cur_time}")
        if len(self.task_list) == 0:
            now = datetime.now()
            cur_time = now.strftime("%H:%M:%S")
            print(f"end find_builds_for_host(false) at {cur_time}")
            return False

        build_id = self.task_list[0].build_info["build_id"]
        all_logs = session.getBuildLogs(build_id)
        hw_log = None
        for log in all_logs:
            if log["name"] == "hw_info.log" and log["dir"] in self.hw_dict["arches"]:
                hw_log = log
                break

        # Check if hw_logs has been assigned
        if hw_log == None:
            now = datetime.now()
            cur_time = now.strftime("%H:%M:%S")
            print(f"end find_builds_for_host(false) at {cur_time}")
            return False

        # Make URL for hw_log and use requests.get(url) to download log
        mykoji = koji.get_profile_module("brew")
        url = os.path.join(mykoji.config.topurl, hw_log["path"])
        response = requests.get(url)
        hw_log_str = response.text

        hw_log_lines = hw_log_str.split("\n")
        hw_log_lines = [re.sub(r"\s+", ",", line) for line in hw_log_lines]

        for line in hw_log_lines:
            line_split = line.split(",")

            if line_split[0] == "CPU(s):":
                self.hw_dict["CPU(s)"] = int(line_split[1])
                continue
            if line_split[0] == "Mem:":
                self.hw_dict["Ram"] = int(line_split[1])
                continue
            disk_match = re.match(r"^/", line_split[0])
            if disk_match:
                self.hw_dict["Disk"] = line_split[1]
                continue

        now = datetime.now()
        cur_time = now.strftime("%H:%M:%S")
        print(f"end find_builds_for_host(true) at {cur_time}")
        return True


class task:
    """
    Brew task
    """

    def __init__(self, task_id, parent_id, build_info):
        self.task_id = int(task_id)
        self.parent_id = int(parent_id)
        self.build_info = build_info

    def __str__(self):
        """
        Returns a string for a task object
        """
        task_str = f"Task ID: {self.task_id}\nParent ID: {self.parent_id}\nBuild Info: {self.build_info}"
        return task_str


def compare_hosts(hostA, hostB):
    """
    Compares two hosts, if they are similar it will return True, and False otherwise
    """
    similar = True

    if hostA.hw_dict["Ram"] != None and hostB.hw_dict["Ram"] != None:
        a_ram = int(hostA.hw_dict["Ram"])
        b_ram = int(hostB.hw_dict["Ram"])
        ram_tol = 4000000  # 4gb tolerance for ram similarity
        if b_ram < a_ram - ram_tol or b_ram > a_ram + ram_tol:
            similar = False

    if hostA.hw_dict["CPU(s)"] != hostB.hw_dict["CPU(s)"]:
        similar = False

    return similar


def collect_channels(session):
    """
    Collects brew channels from brew and creates
    objects for them

    returns a list of channel objects
    """
    channel_objects = []
    brew_channels = session.listChannels()

    for brew_channel in brew_channels:
        channel_objects.append(channel(brew_channel["name"], brew_channel["id"]))

    return channel_objects


if __name__ == "__main__":
    mykoji = koji.get_profile_module("brew")

    opts = vars(mykoji.config)
    session = mykoji.ClientSession(mykoji.config.server, opts)

    channels = collect_channels(session)

    rhel8_beefy = channels[30]
    rhel8_beefy.collect_hosts(session)

    for hosts in rhel8_beefy.host_list:
        hosts.find_builds_for_host(session)
        hosts.get_hw_info(session)
        print(f"collected host: {hosts.id}")

    rhel8_beefy.config_check()

    print(f"rhel8_beefy contains {len(rhel8_beefy.host_list)} hosts")
    print(
        f"rhel8_beefy was divided in to {len(rhel8_beefy.config_groups)} configuration groups based on CPU count and Ram"
    )
    for index, sub_list in enumerate(rhel8_beefy.config_groups):
        print(
            f"\n================================ Group {index}/{len(rhel8_beefy.config_groups)} ================================"
        )
        for hosts in sub_list:
            print(
                f"ID: {hosts.id} arches: {hosts.hw_dict['arches']} CPU(s): {hosts.hw_dict['CPU(s)']} Ram: {hosts.hw_dict['Ram']} Disk: {hosts.hw_dict['Disk']} Kernel: {hosts.hw_dict['Kernel']} O/S: {hosts.hw_dict['Operating System']}"
            )
    print(rhel8_beefy)
