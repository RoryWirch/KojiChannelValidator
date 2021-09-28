import koji


class channel:
    """
    Brew build channel
    """

    def __init__(self, name, id):
        self.name = str(name)
        self.id = int(id)
        self.host_list = []

    def collect_hosts(self, session):
        """
        Finds all the hosts for the channel and adds them to host_list
        """
        list_host_response = session.listHosts(channelID=self.id)

        for hosts in list_host_response:
            self.host_list.append(
                host(name=hosts["name"], id=hosts["id"], enabled=hosts["enabled"])
            )


class host:
    """
    Brew build host
    """

    def __init__(self, name, id, enabled):
        self.name = str(name)
        self.id = int(id)
        self.enabled = bool(enabled)
        self.task_list = []

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
            queryOpts = {"limit": 10,"order": "-completion_time"}
            tasks = session.listTasks(opts, queryOpts)
            for brew_task in tasks:
                parent_id = brew_task["parent"]
                build = session.listBuilds(taskID=parent_id)
                if len(build) != 0:
                    self.task_list.append(task(
                                            task_id = brew_task["id"],
                                            parent_id=brew_task["parent"],
                                            build_info=build[0]
                    ))
                    break
        else:
            self.task_list.append(task(
                                    task_id=tasks[0]["id"],
                                    parent_id=tasks[0]["parent"],
                                    build_info=tasks[0]
            ))

class task:
    """
    Brew task
    """

    def __init__(self, task_id, parent_id, build_info):
        self.task_id = int(task_id)
        self.parent_id = int(parent_id)
        self.build_info = build_info


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
        for host in channel.host_list:
            host.find_builds_for_host(session)
