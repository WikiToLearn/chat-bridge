#!/usr/bin/env python3
from WtlChatAdapters.WtlChatAdapter import WtlChatAdapter
import time

import irc.bot

class IrcBridgeBot(irc.bot.SingleServerIRCBot):
    def __init__(self, adapter_name, event_emitter, server, port, nickname):
        irc.bot.SingleServerIRCBot.__init__(self, [(server, port)], nickname, nickname)
        self.channels_to_join = []
        self.adapter_name = adapter_name
        self.event_emitter = event_emitter

    def on_nicknameinuse(self, c, e):
        c.nick(c.get_nickname() + "_")

    def on_welcome(self, c, e):
        for channel_id in self.channels_to_join:
            c.join(channel_id)

    def on_privmsg(self, c, e):
        message_event = {"adapter_name":self.adapter_name}
        message_event['channel_id'] = e.target
        message_event['from'] = e.source
        message_event['text'] = " ".join(e.arguments)
        self.event_emitter.emit('message',message_event)

    def on_pubmsg(self, c, e):
        message_event = {"adapter_name":self.adapter_name}
        message_event['channel_id'] = e.target
        message_event['from'] = e.source
        message_event['text'] = " ".join(e.arguments)
        self.event_emitter.emit('message',message_event)

    def on_disconnect(self, c, e):
        print(e)

    def add_join_channels(self,channel_id):
        self.channels_to_join.append(channel_id)

class Irc(WtlChatAdapter):

    def __init__(self, adapter_name,event_emitter, server, port, nickname):
        WtlChatAdapter.__init__(self,adapter_name,event_emitter)
        self.ircbot = IrcBridgeBot(adapter_name,event_emitter,server, port, nickname)

    def run(self):
        self.ircbot.start()
        self.stop()

    def send_msg(self,channel_id,msg):
        self.ircbot.connection.privmsg(channel_id, msg.replace('\n','[\\n]'))

    def use_channel(self,channel_id):
        self.ircbot.add_join_channels(channel_id)
        return True

    def stop(self):
        self.ircbot.disconnect()
        self.ircbot.die()
        WtlChatAdapter.stop(self)
