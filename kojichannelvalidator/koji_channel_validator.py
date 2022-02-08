import os
import requests
import koji
import re
import logging


class Channel:
    """
    Koji build channel
    """

    def __init__(self, name, id, cpus=8):
        self.name = str(name)
        self.id = int(id)
        self.host_list = []
        self.config_groups = []
        self.min_cpus = cpus

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
                Host(
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

    def is_valid(self):
        """
        Checks that all hosts in self.config_groups has a valid cpu count
        """
        flag = True
        for group in self.config_groups:
            for host in group:
                try:
                    if host.hw_dict["CPU(s)"] < self.min_cpus:
                        logging.info(
                            f'Host: {host.id} CPU(s): {host.hw_dict["CPU(s)"]} does not meet the minimum CPU count of {self.min_cpus}'
                        )
                        flag = False
                except TypeError:
                    logging.error(
                        f'TYPE ERROR Host: {host.id} CPU count "{type(host.hw_dict["CPU(s)"])}"cannot be compared to type Int'
                    )
                    logging.info(
                        "Note that a CPU(s) value of None may mean a hw_info.log was not found for the host."
                    )
                    flag = False

        return flag


class Host:
    """
    Koji build host
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
        logging.info(
            f"\n===========================================================================\nStarting find_builds_for_host for host: {self.id}"
        )
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
            logging.info("NO TASKS FOUND. No tasks found on host %s", self.id)
            return

        # Check build info for task and check for scratch build
        parent_id = tasks[0]["parent"]
        build = session.listBuilds(taskID=parent_id)
        # Scratch build is found if build info is empty. Retry query opts
        # for past 10 builds for the host
        if len(build) == 0:
            queryOpts = {"limit": 10, "order": "-completion_time"}

            tasks = session.listTasks(opts, queryOpts)
            for koji_task in tasks:
                parent_id = koji_task["parent"]

                build = session.listBuilds(taskID=parent_id)
                if len(build) != 0:
                    logging.info("TASK FOUND. Task found for host: %s", self.id)
                    self.task_list.append(
                        Task(
                            task_id=koji_task["id"],
                            parent_id=koji_task["parent"],
                            build_info=build[0],
                        )
                    )
                    break
        else:
            logging.info("TASK FOUND. Task found for host %s", self.id)
            self.task_list.append(
                Task(
                    task_id=tasks[0]["id"],
                    parent_id=tasks[0]["parent"],
                    build_info=build[0],
                )
            )
        logging.info(f"Successful return from find_builds_for_hosts")

    def get_hw_info(self, session):
        """
        Gets hardware information for a host. Downloads hw_info.log for the
        hosts architecture and pulls hardware information from the log.
        """
        logging.info(
            f"Start get_hw_info for host {self.id} using task:\n\t{self.task_list[0]}"
        )
        if len(self.task_list) == 0:
            logging.info(
                f"No tasks found in the tasklist of host {self.id}. Unable to find hw_info log without a task"
            )
            return False

        build_id = self.task_list[0].build_info["build_id"]
        all_logs = session.getBuildLogs(build_id)
        hw_log = None
        for log in all_logs:
            if log["name"] == "hw_info.log" and log["dir"] in self.hw_dict["arches"]:
                hw_log = log
                break
            elif log["name"] == "hw_info.log" and log["dir"] == "noarch":
                hw_log = log
                break

        # Check if hw_logs has been assigned
        if hw_log == None:
            logging.info(
                f"No hw_log found for host: {self.id} all logs for build: {all_logs}"
            )
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

        logging.info("Successful return from get_hw_info")
        return True


class Task:
    """
    Koji task
    """

    def __init__(self, task_id, parent_id, build_info):
        self.task_id = int(task_id)
        self.parent_id = int(parent_id)
        self.build_info = build_info

    def __str__(self):
        """
        Returns a string for a task object
        """
        task_str = f"Task ID: {self.task_id}\n\tParent ID: {self.parent_id}\n\tBuild Info: {self.build_info}"
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
    Collects koji channels from koji and creates
    objects for them

    returns a list of channel objects
    """
    channel_objects = []
    koji_channels = session.listChannels()

    for koji_channel in koji_channels:
        channel_objects.append(Channel(koji_channel["name"], koji_channel["id"]))

    return channel_objects


def check(args):
    if args.log:
        logging.basicConfig(
            format="%(asctime)s %(levelname)-8s %(message)s",
            level=logging.INFO,
            datefmt="%Y-%m-%d %H:%M:%S",
        )
    channel_name = args.channel

    mykoji = koji.get_profile_module("brew")

    opts = vars(mykoji.config)
    session = mykoji.ClientSession(mykoji.config.server, opts)

    channel_info = session.getChannel(channel_name)
    mychannel = Channel(channel_info["name"], channel_info["id"])
    mychannel.collect_hosts(session)

    for hosts in mychannel.host_list:
        hosts.find_builds_for_host(session)
        hosts.get_hw_info(session)

    mychannel.config_check()

    print(f"{mychannel.name} contains {len(mychannel.host_list)} hosts")
    print(
        f"{mychannel.name} was divided in to {len(mychannel.config_groups)} configuration groups based on CPU count and Ram"
    )
    for index, sub_list in enumerate(mychannel.config_groups):
        print(
            f"\n================================ Group {index+1}/{len(mychannel.config_groups)} ================================"
        )
        for hosts in sub_list:
            print(
                f"ID: {hosts.id} arches: {hosts.hw_dict['arches']} CPU(s): {hosts.hw_dict['CPU(s)']} Ram: {hosts.hw_dict['Ram']} Disk: {hosts.hw_dict['Disk']} Kernel: {hosts.hw_dict['Kernel']} O/S: {hosts.hw_dict['Operating System']}"
            )

    if mychannel.is_valid():
        return 0

    return 1
