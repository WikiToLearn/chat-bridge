#!/usr/bin/env python3
import wtl
import requests
import sys
import time
from pyee import EventEmitter

from WtlChatAdapters.RocketChat import RocketChat
from WtlChatAdapters.Telegram import Telegram
from WtlChatAdapters.Irc import Irc

event_emitter = EventEmitter()

adapters = wtl.load_config(config_prefix="adapters",config_dir="/etc/chat-bridge/")
bridges = wtl.load_config(config_prefix="bridges",config_dir="/etc/chat-bridge/")

chat_adapters = {}
for adapter in adapters:
    if adapters[adapter]['type'] == "rocketchat":
        chat_adapters[adapter] = RocketChat(adapter, event_emitter, baseurl=adapters[adapter][
                                            'baseurl'], username=adapters[adapter]['username'], password=adapters[adapter]['password'])
        for room in chat_adapters[adapter].joined_rooms():
            print(room['_id'])
            if 'name' in room:
                print(room['name'])
            print("")
    elif adapters[adapter]['type'] == "telegram":
        chat_adapters[adapter] = Telegram(
            adapter, event_emitter, adapters[adapter]['token'])
    elif adapters[adapter]['type'] == "irc":
        chat_adapters[adapter] = Irc(adapter, event_emitter, adapters[adapter]['server'], adapters[adapter]['port'], adapters[adapter]['nickname'])
    else:
        print("Adapter type {} not supported".format(
            adapters[adapter]['type']))
        sys.exit(1)

all_adapters_ok = True
for bridge in bridges:
    print("Chack adapters for: {}".format(bridge))
    for channel in bridges[bridge]:
        adapter_ok = channel['adapter_name'] in adapters
        adapter_ok = chat_adapters[channel['adapter_name']
                      ].use_channel(channel['channel_id']) and adapter_ok
        all_adapters_ok = all_adapters_ok and adapter_ok
        print("> {} ({}): {}".format(
            channel['adapter_name'], channel['channel_id'], adapter_ok))
    print()

if not all_adapters_ok:
    print("Some adapter is not supported, check your config")
    sys.exit(1)

for adapter in chat_adapters:
    chat_adapters[adapter].start()


@event_emitter.on('message')
def event_handler(message):
    dests = []
    print("From channel: {}".format(message['channel_id']))
    print("From username: {}".format(message['from']))
    print("Text: {}".format(message['text']))

    for bridge_name in bridges:
        from_label = None
        send_to_this_bdirge = False
        this_bridge_dests = []
        for channel in bridges[bridge_name]:
            if channel['channel_id'] == message['channel_id'] and channel['adapter_name'] == message['adapter_name']:
                send_to_this_bdirge = True
                from_label = channel['from_channel_label']
            else:
                this_bridge_dests.append(channel)
        if send_to_this_bdirge:
            print("Send using: {}".format(bridge_name))
        if send_to_this_bdirge:
            for dest_channel in this_bridge_dests:
                print("Sending to {}".format(dest_channel['channel_id']))
                chat_adapters[dest_channel['adapter_name']].send_msg(dest_channel['channel_id'], message[
                    'from'] + " (" + from_label + "): " + message['text'])
    print()

print("Running...")
running = True
while running:
    running = False
    allRunning = True
    for adapter in chat_adapters:
        running = running or chat_adapters[adapter].isAlive()
        allRunning = allRunning and chat_adapters[adapter].isAlive()

    for adapter in chat_adapters:
        if not allRunning and chat_adapters[adapter].isAlive():
            chat_adapters[adapter].stop()
            print("Waiting for '{}' to stop".format(adapter))
            chat_adapters[adapter].join()
    try:
        time.sleep(1)
    except KeyboardInterrupt as ki:
        running = False


for adapter in chat_adapters:
    if chat_adapters[adapter].isAlive():
        chat_adapters[adapter].stop()
        print("Waiting for '{}' to stop".format(adapter))
        chat_adapters[adapter].join()

print("End")
