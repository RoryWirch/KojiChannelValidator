import os
import requests
import koji
from pprint import pprint


class channel:
    """
    Brew build channel
    """

    def __init__(self, name, id):
        self.name = str(name)
        self.id = int(id)
        self.host_list = []

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


class host:
    """
    Brew build host
    """

    def __init__(self, name, id, enabled, arches, description):
        self.name = str(name)
        self.id = int(id)
        self.enabled = bool(enabled)
        self.task_list = []
        hw_keys = ["arches", "CPU(s)", "Ram", "Disk", "Kernel", "Operating System"]
        self.hw_dict = {key: None for key in hw_keys}
        self.hw_dict["arches"] = arches.split(" ")
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

    def get_hw_info(self, session):
        """
        Gets hardware information for a host. Downloads hw_info.log for the
        hosts architecture and pulls hardware information from the log.
        """
        if len(self.task_list) == 0:
            return False

        build_id = self.task_list[0].build_info["build_id"]
        all_logs = session.getBuildLogs(build_id)

        for log in all_logs:
            if log["name"] == "hw_info.log" and log["dir"] in self.hw_dict["arches"]:
                hw_log = log
                break

        # Make URL for hw_log and use requests.get(url) to download log
        mykoji = koji.get_profile_module("brew")
        url = os.path.join(mykoji.config.topurl, hw_log["path"])
        response = requests.get(url)
        hw_log_str = response.text()

        for line in hw_log_str.split("\n"):
            line_split = line.split(":")
            if line_split[0] == "CPU(s)":
                cpu_split = line.split(":")
                cpu_split = cpu_split.strip("")
                self.hw_dict["CPU(s)"] = cpu_split[1]
                continue


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

    for channel in channels:
        channel.collect_hosts(session)
        for hosts in channel.host_list:
            # hosts.find_builds_for_host(session)
            print(hosts)
        print(channel)

    # rhel8 = channels[20]  # should be channel 21, rhel8
    # rhel8.collect_hosts(session)

    # for hosts in rhel8.host_list:
    #     hosts.find_builds_for_host(session)
    #     print(hosts)

    # print(rhel8)
