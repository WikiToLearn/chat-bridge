#!/usr/bin/env python3
from WtlChatAdapters.WtlChatAdapter import WtlChatAdapter
import time

import irc.bot

class IrcBridgeBot(irc.bot.SingleServerIRCBot):
    def __init__(self, server, port, nickname):
        irc.bot.SingleServerIRCBot.__init__(self, [(server, port)], nickname, nickname)
        self.channels_to_join = []

    def on_nicknameinuse(self, c, e):
        print("nicknameinuse")
        c.nick(c.get_nickname() + "_")
        print(e)

    def on_welcome(self, c, e):
        print("welcome")
        for channel_id in self.channels_to_join:
            c.join(channel_id)
        print(e)

    def on_join(self, c, e):
        print("joined to " + e.target)
        print(e)

    def on_privmsg(self, c, e):
        print("privmsg")
        print(e)
        #c.notice(e.source.nick, "CIAO 1")
        #c.privmsg(e.source.nick,"CIAO 2")

    def on_pubmsg(self, c, e):
        print("pubmsg")
        print(e.source)
        print(e.target)
        print(" ".join(e.arguments))
        c.privmsg(e.target, "This: {}".format(" ".join(e.arguments)))
        print(e)

    def on_dccmsg(self, c, e):
        print("dccmsg")
        print(e)

    def on_ctcp(self, c, e):
        print("ctcp")
        print(e)

    def on_dccmsg(self, c, e):
        print("ccmsg")
        print(e)

    def on_disconnect(self, c, e):
        print(e)

    def add_join_channels(self,channel_id):
        self.channels_to_join.append(channel_id)

class Irc(WtlChatAdapter):

    def __init__(self, adapter_name,event_emitter, server, port, nickname):
        WtlChatAdapter.__init__(self,adapter_name,event_emitter)
        self.ircbot = IrcBridgeBot(server, port, nickname)

    def run(self):
        self.ircbot.start()
        self.stop()

    def send_msg(self,channel_id,msg):
        self.ircbot.connection.privmsg(channel_id, msg)

    def use_channel(self,channel_id):
        self.ircbot.add_join_channels(channel_id)
        return True

    def stop(self):
        self.ircbot.die()
        WtlChatAdapter.stop(self)
