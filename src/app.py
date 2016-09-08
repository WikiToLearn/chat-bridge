#!/usr/bin/env python3
import requests
import yaml
import sys

from WtlChatAdapters.RocketChat import RocketChat
from WtlChatAdapters.Telegram   import Telegram

stream_adapters = open('/etc/chat-bridge/adapters.yml', 'r')
adapters = yaml.load(stream_adapters, Loader=yaml.Loader)
stream_adapters.close()

stream_bridges = open('/etc/chat-bridge/bridges.yml', 'r')
bridges = yaml.load(stream_bridges, Loader=yaml.Loader)
stream_bridges.close()

all_adapters_ok = True
for bridge in bridges:
    print("Chack adapters for: {}".format(bridge))
    for channel in bridges[bridge]:
        adapter_ok = channel['adapter_name'] in adapters
        all_adapters_ok = all_adapters_ok and adapter_ok
        print("> {} ({}): {}".format(channel['adapter_name'],channel['channel_id'],adapter_ok))
    print()

if not all_adapters_ok:
    print("Some adapter is not supported, check your config")
    sys.exit(1)

chat_adapters = {}
for adapter in adapters:
    if adapters[adapter]['type'] == "rocketchat":
        chat_adapters[adapter] = RocketChat(adapter,baseurl=adapters[adapter]['baseurl'], username=adapters[adapter]['username'], password=adapters[adapter]['password'])
    elif adapters[adapter]['type'] == "telegram":
        chat_adapters[adapter] = Telegram(adapter,adapters[adapter]['token'])
    else:
        print("Adapter type {} not supported".format(adapters[adapter]['type']))
        sys.exit(1)

for adapter in chat_adapters:
    chat_adapters[adapter].start()
    chat_adapters[adapter].join()
