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
            self.host_list.append(host(name=hosts["name"],
                                        id=hosts["id"],
                                        enabled=hosts["enabled"]))


class host:
    """
    Brew build host
    """

    def __init__(self, name, id, enabled):
        self.name = str(name)
        self.id = int(id)
        self.enabled = bool(enabled)
        self.task_list = []


class task:
    """
    Brew task
    """

    def __init__(self, task_id, parent_id):
        self.task_id = int(task_id)
        self.parent_id = int(parent_id)
        self.build_info = []


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