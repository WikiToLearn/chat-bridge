#!/usr/bin/env python3

import irc.bot

server = "chat.freenode.net"
port = 6665
nickname = "wikitolearnbot"

class TestBot(irc.bot.SingleServerIRCBot):
    def __init__(self, server, port, nickname):
        irc.bot.SingleServerIRCBot.__init__(self, [(server, port)], nickname, nickname)

    def on_nicknameinuse(self, c, e):
        print("nicknameinuse")
        c.nick(c.get_nickname() + "_")
        print(e)

    def on_welcome(self, c, e):
        print("welcome")
        print(c.join("#wikitolearn-tech"))
        print(e)

    def on_join(self, c, e):
        print("joined")
        print(e)

    def on_privmsg(self, c, e):
        print("privmsg")
        print(e)
        c.notice(e.source.nick, "CIAO 1")
        c.privmsg(e.source.nick,"CIAO 2")

    def on_pubmsg(self, c, e):
        print("pubmsg")
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
        sys.exit(0)


i = TestBot(server, port, nickname)
i.start()
