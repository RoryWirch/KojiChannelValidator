import os
import requests
import koji




mykoji = koji.get_profile_module('brew')

opts = vars(mykoji.config)
session = mykoji.ClientSession(mykoji.config.server, opts)

channels = session.listChannels()

for channel in channels:
    channel_name = channel['name']
    
    hosts = session.listHosts(channelID=channel_name)

    print(f"\nchannel name: {channel_name}")

    for host in hosts:
        host_name = host['name']
        print(f"\t{host_name}")