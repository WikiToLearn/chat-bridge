#!/usr/bin/env python3
from WtlChatAdapters.WtlChatAdapter import WtlChatAdapter
import telegram

class Telegram(WtlChatAdapter):

    def __init__(self, adapter_name, token):
        WtlChatAdapter.__init__(self,adapter_name)
        self.bot = telegram.Bot(token)

    def run(self):
        pass
