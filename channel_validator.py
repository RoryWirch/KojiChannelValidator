import koji


class channel:
    """
    Brew build channel
    """

    def __init__(self, name, id):
        self.name = str(name)
        self.id = int(id)
        self.host_list = []

    def get_name(self):
        return self.name

    def get_id(self):
        return self.id

    def get_host_list(self):
        return self.host_list
 


class host:
    """
    Brew build host
    """

    def __init__(self, name, id, enabled):
        self.name = str(name)
        self.id = int(id)
        self.enabled = bool(enabled)
        self.task_list = []
    
    def get_name(self):
        return self.name

    def get_id(self):
        return self.id

    def get_enabled(self):
        return self.enabled

    def get_task_list(self):
        return self.get_task_list    


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
