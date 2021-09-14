import koji
from pprint import pprint

mykoji = koji.get_profile_module('brew')

opts = vars(mykoji.config)
session = mykoji.ClientSession(mykoji.config.server, opts)

channels = session.listChannels()

for channel in channels:
    channel_name = channel['name']
    hosts = session.listHosts(channelID=channel_name)

    print(f"\nchannel name: {channel_name}")

    for host in hosts:
        #check if host is enabled
        if host['enabled']:
            host_name = host['name']
            host_id = host['id']
            print(f"\t{host_name}")
            print(f"\thostID: {host_id}")

            opts = {
                'host_id': host_id,
                'method': 'buildArch',
                'state': [koji.TASK_STATES['CLOSED']],
                'decode': 'True'
            }
            queryOpts={'limit':1, 'order':'-completion_time'}

            tasks = session.listTasks(opts, queryOpts)

            # check if there are tasks returned for the host
            if len(tasks) > 0:
                parent_id = tasks[0]['parent']
                build_info = session.listBuilds(taskID=parent_id)

                # check for scratch build
                if len(build_info) == 0: 
                    print(f"\t\tscratch build ID: {parent_id}")
                
            else:
                print(f"\tNo tasks found on {host_name}:{host_id}")