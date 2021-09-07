import os
import requests
import koji

mykoji = koji.get_profile_module('brew')

opts = vars(mykoji.config)
session = mykoji.ClientSession(mykoji.config.server, opts)

channels = session.listChannels()

for channel in channels:
    print(channel)